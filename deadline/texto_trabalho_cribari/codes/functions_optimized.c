#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>

// Function prototypes
double* moving_block_bootstrap(double* log_returns, int n_returns, int n_bootstrap, 
                              int sample_size, int block_size, int seed);
double* monte_carlo_simulation(double S0, double* bootstrap_samples, 
                              int n_bootstrap, int sample_size, int iterations, int seed);
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

/**
 * Moving Block Bootstrap Implementation
 * Generates bootstrap samples preserving temporal dependencies
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
    
    // Generate bootstrap samples
    for (int bootstrap_idx = 0; bootstrap_idx < n_bootstrap; bootstrap_idx++) {
        int sample_idx = 0;
        
        while (sample_idx < sample_size) {
            // Randomly select a block
            int block_start = random_int(n_blocks);
            
            // Copy block to sample
            for (int i = 0; i < block_size && sample_idx < sample_size; i++) {
                bootstrap_samples[bootstrap_idx * sample_size + sample_idx] = 
                    log_returns[block_start + i];
                sample_idx++;
            }
        }
    }
    
    return bootstrap_samples;
}

/**
 * Monte Carlo Simulation Implementation
 * Each iteration uses one complete bootstrap sample as temporal path
 * Returns both final prices and complete price paths
 */
double* monte_carlo_simulation(double S0, double* bootstrap_samples, 
                              int n_bootstrap, int sample_size, int iterations, int seed) {
    
    // Random seed already set in bootstrap function
    
    if (iterations > n_bootstrap) {
        printf("WARNING: More iterations (%d) than bootstrap samples (%d)\n", iterations, n_bootstrap);
    }
    
    // Allocate memory for final prices (first iterations elements)
    // and price paths (remaining iterations * sample_size elements)
    double* results = allocate_array(iterations + iterations * sample_size);
    if (!results) {
        printf("ERROR: Memory allocation failed\n");
        return NULL;
    }
    
    // Generate Monte Carlo paths
    for (int iter = 0; iter < iterations; iter++) {
        double current_price = S0;
        
        // Select ONE complete bootstrap sample (preserving temporal structure)
        int bootstrap_idx = random_int(n_bootstrap);
        
        // Store initial price
        results[iterations + iter * sample_size] = S0;
        
        // Use this bootstrap sample sequentially as a complete temporal path
        for (int t = 0; t < sample_size; t++) {
            double log_return = bootstrap_samples[bootstrap_idx * sample_size + t];
            current_price *= exp(log_return);
            
            // Store price at each time step
            results[iterations + iter * sample_size + t] = current_price;
        }
        
        // Store final price
        results[iter] = current_price;
    }
    
    return results;
}

/**
 * Calculate portfolio returns for given weights
 */
double* calculate_portfolio_returns(double* weights, double* arrival_values, 
                                  int n_assets, int n_simulations) {
    double* portfolio_values = allocate_array(n_simulations);
    if (!portfolio_values) return NULL;
    
    for (int sim = 0; sim < n_simulations; sim++) {
        double value = 0.0;
        for (int asset = 0; asset < n_assets; asset++) {
            value += weights[asset] * arrival_values[sim * n_assets + asset];
        }
        portfolio_values[sim] = value;
    }
    
    return portfolio_values;
}

/**
 * Calculate Sharpe ratio
 */
double calculate_sharpe_ratio(double* portfolio_values, int n_values, double risk_free_rate) {
    if (n_values <= 1) return 0.0;
    
    // Calculate mean and standard deviation
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

/**
 * Negative Sharpe ratio for optimization (since we minimize)
 */
double negative_sharpe_ratio(double* weights, double* arrival_values, int n_assets, 
                           int n_simulations, double risk_free_rate) {
    double* portfolio_values = calculate_portfolio_returns(weights, arrival_values, 
                                                         n_assets, n_simulations);
    if (!portfolio_values) return 1e6;
    
    double sharpe = calculate_sharpe_ratio(portfolio_values, n_simulations, risk_free_rate);
    free(portfolio_values);
    
    return -sharpe; // Negative because we minimize
}

/**
 * Newton-Raphson Portfolio Optimization
 * Optimizes portfolio weights to maximize Sharpe ratio
 */
double* optimize_portfolio_newton_raphson(double* arrival_values, int n_assets, int n_simulations, 
                                        double* initial_weights, double risk_free_rate, 
                                        int max_iterations, double tolerance) {
    
    double* weights = allocate_array(n_assets);
    if (!weights) return NULL;
    
    // Copy initial weights
    for (int i = 0; i < n_assets; i++) {
        weights[i] = initial_weights[i];
    }
    
    // Newton-Raphson optimization
    for (int iter = 0; iter < max_iterations; iter++) {
        // Calculate gradient and Hessian numerically
        double** hessian = allocate_matrix(n_assets, n_assets);
        double* gradient = allocate_array(n_assets);
        
        if (!hessian || !gradient) {
            if (hessian) free_matrix(hessian, n_assets);
            if (gradient) free(gradient);
            free(weights);
            return NULL;
        }
        
        double h = 1e-6; // Step size for numerical differentiation
        
        // Calculate gradient and Hessian
        for (int i = 0; i < n_assets; i++) {
            // Forward step
            weights[i] += h;
            double f_forward = negative_sharpe_ratio(weights, arrival_values, n_assets, n_simulations, risk_free_rate);
            
            // Backward step
            weights[i] -= 2 * h;
            double f_backward = negative_sharpe_ratio(weights, arrival_values, n_assets, n_simulations, risk_free_rate);
            
            // Restore
            weights[i] += h;
            
            // Gradient
            gradient[i] = (f_forward - f_backward) / (2 * h);
            
            // Hessian diagonal
            hessian[i][i] = (f_forward + f_backward - 2 * negative_sharpe_ratio(weights, arrival_values, n_assets, n_simulations, risk_free_rate)) / (h * h);
            
            // Add regularization
            hessian[i][i] += 1e-6;
        }
        
        // Off-diagonal Hessian elements (simplified)
        for (int i = 0; i < n_assets; i++) {
            for (int j = 0; j < n_assets; j++) {
                if (i != j) hessian[i][j] = 0.0;
            }
        }
        
        // Solve linear system: H * delta = -gradient
        double* delta = allocate_array(n_assets);
        if (!delta) {
            free_matrix(hessian, n_assets);
            free(gradient);
            free(weights);
            return NULL;
        }
        
        // Simple diagonal solver (since Hessian is diagonal)
        for (int i = 0; i < n_assets; i++) {
            delta[i] = -gradient[i] / hessian[i][i];
        }
        
        // Update weights with line search
        double alpha = 1.0;
        double f_current = negative_sharpe_ratio(weights, arrival_values, n_assets, n_simulations, risk_free_rate);
        
        // Backtracking line search
        for (int ls_iter = 0; ls_iter < 10; ls_iter++) {
            // Update weights
            for (int i = 0; i < n_assets; i++) {
                weights[i] += alpha * delta[i];
            }
            
            // Project to simplex (weights sum to 1, all >= 0)
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
                break; // Accept step
            }
            
            alpha *= 0.5; // Reduce step size
        }
        
        // Check convergence
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
 * Utility Functions
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

/**
 * Test function for compilation verification
 */
int main() {
    return 0;
} 