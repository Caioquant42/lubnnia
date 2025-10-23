export function formatNumber(p_value: number, decimalPlaces = 2): string {
  return p_value.toLocaleString('pt-BR', {
    style: 'decimal',
    minimumFractionDigits: decimalPlaces,
    maximumFractionDigits: decimalPlaces,
  });
}