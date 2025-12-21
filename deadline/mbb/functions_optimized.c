#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>

// Protótipos de função
double* moving_block_bootstrap(double* log_returns, int n_returns, int n_bootstrap, 
                              int sample_size, int block_size, int seed);
double* monte_carlo_simulation(double S0, double* bootstrap_samples, 
                              int n_bootstrap, int sample_size, int iterations);
double* optimize_portfolio_newton_raphson(double* arrival_values, int n_assets, int n_simulations, 
                                        double* initial_weights, double risk_free_rate, 
                                        int max_iterations, double tolerance);

// Utility functions
double* allocate_array(int size);
double** allocate_matrix(int rows, int cols);
void free_matrix(double** matrix, int rows);
int random_int(int max_val);
double random_double();
int invert_matrix(double** matrix, double** inverse, int n);

/*
 * Implementação do MBB (Moving Block Bootstrap)
 * Gera amostras bootstrap preservando dependências temporais
 */
double* moving_block_bootstrap(double* log_returns, int n_returns, int n_bootstrap, 
                              int sample_size, int block_size, int seed) {
    
    // Set random seed only once at the beginning
    static int seed_set = 0;
    if (seed > 0 && !seed_set) {
        srand(seed);
        seed_set = 1;
    }
    
    if (n_returns < block_size) {
        printf("ERROR: Time series length (%d) must be >= block size (%d)\n", n_returns, block_size);
        return NULL;
    }
    
    int n_blocks = n_returns - block_size + 1;
    double* bootstrap_samples = allocate_array(n_bootstrap * sample_size);
    
    if (!bootstrap_samples) {
        printf("ERROR: Memory allocation failed\n");
        return NULL;
    }
    
    // Gera amostras bootstrap
    for (int bootstrap_idx = 0; bootstrap_idx < n_bootstrap; bootstrap_idx++) {
        int sample_idx = 0;
        
        while (sample_idx < sample_size) {
            // Seleciona bloco aleatoriamente
            int block_start = random_int(n_blocks);
            
            // Copia bloco para a amostra
            for (int i = 0; i < block_size && sample_idx < sample_size; i++) {
                bootstrap_samples[bootstrap_idx * sample_size + sample_idx] = 
                    log_returns[block_start + i];
                sample_idx++;
            }
        }
    }
    
    return bootstrap_samples;
}

/*
 * Implementação da simulação por Monte Carlo
 * (Cada iteração  usa uma amostra bootstrap completa como trajetória temporal)
 */
double* monte_carlo_simulation(double S0, double* bootstrap_samples, 
                              int n_bootstrap, int sample_size, int iterations) {
    
    // Seed aleatória já definida na função do bootstrap
    
    if (iterations > n_bootstrap) {
        printf("WARNING: More iterations (%d) than bootstrap samples (%d)\n", iterations, n_bootstrap);
    }
    
    double* final_prices = allocate_array(iterations);
    if (!final_prices) {
        printf("ERROR: Memory allocation failed\n");
        return NULL;
    }
    
    // Gera trajetórias por Monte Carlo
    for (int iter = 0; iter < iterations; iter++) {
        double current_price = S0;
        
        // Seleciona UMA amostra bootstrap completa (preservando estrutura temporal)
        int bootstrap_idx = random_int(n_bootstrap);
        
        // Usa esta amostra bootstrap completa sequencialmente como uma trajetória temporal (temporal path) completa
        for (int t = 0; t < sample_size; t++) {
            double log_return = bootstrap_samples[bootstrap_idx * sample_size + t];
            current_price *= exp(log_return);
        }
        
        final_prices[iter] = current_price;
    }
    
    return final_prices;
}

/*
 * Calcula retornos do portfolio para um dado conjunto de pesos
 */
double* calculate_portfolio_returns(double* weights, double* arrival_values, 
                                  int n_assets, int n_simulations) {
    double* portfolio_values = allocate_array(n_simulations);
    if (!portfolio_values) return NULL;
    
	// Itera nas simulações
    for (int sim = 0; sim < n_simulations; sim++) {
        double value = 0.0;
		
		// Itera nos ativos
        for (int asset = 0; asset < n_assets; asset++) {
            value += weights[asset] * arrival_values[sim * n_assets + asset];
        }
        portfolio_values[sim] = value;
    }
    
    return portfolio_values;
}

/*
 * Calcula sharpe-ratio
 */
double calculate_sharpe_ratio(double* portfolio_values, int n_values, double risk_free_rate) {
    if (n_values <= 1) return 0.0;
    
    // Calcula média e desvio-padrão
    double sum = 0.0, sum_sq = 0.0;
    for (int i = 0; i < n_values; i++) {
        sum += portfolio_values[i];
        sum_sq += portfolio_values[i] * portfolio_values[i];
    }
    
    double mean = sum / n_values;
    double variance = sum_sq / n_values - mean * mean;
    double std_dev = sqrt(variance);
    
    if (std_dev == 0.0) return 0.0;
    
    return (mean - risk_free_rate) / std_dev;
}

/*
 Função que retorna o negativo do sharpe-ratio: uma vez que a otimização implementada
 * _minimiza_ funções, deve-se multiplicá-la por -1 para que haja maximização)
 */
double negative_sharpe_ratio(double* weights, double* arrival_values, int n_assets, 
                           int n_simulations, double risk_free_rate) {
    double* portfolio_values = calculate_portfolio_returns(weights, arrival_values, 
                                                         n_assets, n_simulations);
    if (!portfolio_values) return 1e6;
    
    double sharpe = calculate_sharpe_ratio(portfolio_values, n_simulations, risk_free_rate);
    free(portfolio_values);
    
    return -sharpe;
}

/*
 * Otimização do portfolio por Newton-Raphson: otimiza pesos de cada ativo no portfolio de
 * modo a maximizar o sharpe-ratio
 */
double* optimize_portfolio_newton_raphson(double* arrival_values, int n_assets, int n_simulations, 
                                        double* initial_weights, double risk_free_rate, 
                                        int max_iterations, double tolerance) {
    
    double* weights = allocate_array(n_assets);
    if (!weights) return NULL;
    
    // Copia pesos iniciais
    for (int i = 0; i < n_assets; i++) {
        weights[i] = initial_weights[i];
    }
    
    // Otimização por Newton-Raphson
    for (int iter = 0; iter < max_iterations; iter++) {
        
		// Calcula vetor gradiente e matriz Hessiana numericamente por diferenças finitas
        double** hessian = allocate_matrix(n_assets, n_assets);
        double* gradient = allocate_array(n_assets);
        
        if (!hessian || !gradient) {
            if (hessian) free_matrix(hessian, n_assets);
            if (gradient) free(gradient);
            free(weights);
            return NULL;
        }
        
        double h = 1e-6; // Tamanho do intervalo para diferenciação numérica
        
        // Calcula gradiente e Hessiana
        for (int i = 0; i < n_assets; i++) {
			
			//// Gradiente
			
            // f(x+h)
            weights[i] += h;
            double f_forward = negative_sharpe_ratio(weights, arrival_values, n_assets, n_simulations, risk_free_rate);
            
            // f(x-h)
            weights[i] -= 2 * h;
            double f_backward = negative_sharpe_ratio(weights, arrival_values, n_assets, n_simulations, risk_free_rate);
            
            // Restaura valor
            weights[i] += h;
            
            // Gradient
            gradient[i] = (f_forward - f_backward) / (2 * h);
            
			//// Hessiana
			
            // Valores da diagonal principal
            hessian[i][i] = (f_forward + f_backward - 2 * negative_sharpe_ratio(weights, arrival_values, n_assets, n_simulations, risk_free_rate)) / (h * h);
            
            // Adiciona valor do passo
            hessian[i][i] += 1e-6;
        }
        
        // Hessiana: elementos fora da diagonal (versão simplificada)
        for (int i = 0; i < n_assets; i++) {
            for (int j = 0; j < n_assets; j++) {
                if (i != j) hessian[i][j] = 0.0;
            }
        }
        
        //// Resolve sistema linear: H * delta = -gradiente
		
        double* delta = allocate_array(n_assets);
        if (!delta) {
            free_matrix(hessian, n_assets);
            free(gradient);
            free(weights);
            return NULL;
        }
        
        // Uma vez que a Hessiana é diagonal...
        for (int i = 0; i < n_assets; i++) {
            delta[i] = -gradient[i] / hessian[i][i];
        }
        
        // Atualiza pesos com busca-em-linha
        double alpha = 1.0;
        double f_current = negative_sharpe_ratio(weights, arrival_values, n_assets, n_simulations, risk_free_rate);
        
        // Faz backtracking
        for (int ls_iter = 0; ls_iter < 10; ls_iter++) {
			
            // Atualiza pesos
            for (int i = 0; i < n_assets; i++) {
                weights[i] += alpha * delta[i];
            }
            
            // Projeta para simplex (a soma dos pesos é igual a um; então todos são maiores ou igual a zero)
            double sum_weights = 0.0;
            for (int i = 0; i < n_assets; i++) {
                weights[i] = fmax(weights[i], 0.0);
                sum_weights += weights[i];
            }
            
            if (sum_weights > 0) {
                for (int i = 0; i < n_assets; i++) {
                    weights[i] /= sum_weights;
                }
            }
            
            double f_new = negative_sharpe_ratio(weights, arrival_values, n_assets, n_simulations, risk_free_rate);
            
            if (f_new < f_current) {
                // Aceita passo
				break;
            }
            
			// Reduz tamanho do passo
            alpha *= 0.5;
        }
        
        // Checa convergência
        double grad_norm = 0.0;
        for (int i = 0; i < n_assets; i++) {
            grad_norm += gradient[i] * gradient[i];
        }
        grad_norm = sqrt(grad_norm);
        
        if (grad_norm < tolerance) {
            free_matrix(hessian, n_assets);
            free(gradient);
            free(delta);
            break;
        }
        
        free_matrix(hessian, n_assets);
        free(gradient);
        free(delta);
    }
    
    return weights;
}

/**
 * Funções de utilidade
 */
double* allocate_array(int size) {
    return (double*)malloc(size * sizeof(double));
}

double** allocate_matrix(int rows, int cols) {
    double** matrix = (double**)malloc(rows * sizeof(double*));
    if (!matrix) return NULL;
    
    for (int i = 0; i < rows; i++) {
        matrix[i] = (double*)malloc(cols * sizeof(double));
        if (!matrix[i]) {
            free_matrix(matrix, i);
            return NULL;
        }
    }
    
    return matrix;
}

void free_matrix(double** matrix, int rows) {
    if (!matrix) return;
    
    for (int i = 0; i < rows; i++) {
        if (matrix[i]) free(matrix[i]);
    }
    free(matrix);
}

int random_int(int max_val) {
    return rand() % max_val;
}

double random_double() {
    return (double)rand() / RAND_MAX;
}

