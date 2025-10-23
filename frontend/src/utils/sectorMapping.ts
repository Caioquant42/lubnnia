// Brazilian Stock Market Sector Mapping
// Maps long Portuguese sector names to concise labels with icons

export interface SectorMapping {
  shortName: string;
  icon: string;
  color: string;
  description: string;
}

export const SECTOR_MAPPINGS: Record<string, SectorMapping> = {
  // Banking & Financial Services
  "BANCOS": {
    shortName: "Banks",
    icon: "🏦",
    color: "#2563eb",
    description: "Banking institutions"
  },
  "EMP. ADM. PART. - SEGURADORAS E CORRETORAS": {
    shortName: "Insurance",
    icon: "🛡️",
    color: "#3b82f6",
    description: "Insurance and brokerage"
  },
  "SEGURADORAS E CORRETORAS": {
    shortName: "Insurance",
    icon: "🛡️",
    color: "#3b82f6",
    description: "Insurance and brokerage"
  },
  "BOLSAS DE VALORES/MERCADORIAS E FUTUROS": {
    shortName: "Exchange",
    icon: "📈",
    color: "#1d4ed8",
    description: "Stock and commodity exchanges"
  },

  // Energy & Utilities
  "PETRÓLEO E GÁS": {
    shortName: "Oil & Gas",
    icon: "⛽",
    color: "#dc2626",
    description: "Oil and gas companies"
  },
  "EMP. ADM. PART. - PETRÓLEO E GÁS": {
    shortName: "Oil & Gas",
    icon: "⛽",
    color: "#dc2626",
    description: "Oil and gas holding companies"
  },
  "ENERGIA ELÉTRICA": {
    shortName: "Electric",
    icon: "⚡",
    color: "#f59e0b",
    description: "Electric energy companies"
  },
  "EMP. ADM. PART. - ENERGIA ELÉTRICA": {
    shortName: "Electric",
    icon: "⚡",
    color: "#f59e0b",
    description: "Electric energy holding companies"
  },
  "SANEAMENTO, SERV. ÁGUA E GÁS": {
    shortName: "Utilities",
    icon: "💧",
    color: "#0ea5e9",
    description: "Water and sanitation services"
  },

  // Mining & Materials
  "EXTRAÇÃO MINERAL": {
    shortName: "Mining",
    icon: "⛏️",
    color: "#78716c",
    description: "Mineral extraction"
  },
  "EMP. ADM. PART. - EXTRAÇÃO MINERAL": {
    shortName: "Mining",
    icon: "⛏️",
    color: "#78716c",
    description: "Mining holding companies"
  },
  "METALURGIA E SIDERURGIA": {
    shortName: "Steel",
    icon: "🔩",
    color: "#6b7280",
    description: "Metallurgy and steel"
  },
  "PAPEL E CELULOSE": {
    shortName: "Paper",
    icon: "📄",
    color: "#84cc16",
    description: "Paper and pulp"
  },
  "PETROQUÍMICOS E BORRACHA": {
    shortName: "Chemical",
    icon: "🧪",
    color: "#8b5cf6",
    description: "Petrochemicals and rubber"
  },

  // Consumer & Retail
  "COMÉRCIO (ATACADO E VAREJO)": {
    shortName: "Retail",
    icon: "🛒",
    color: "#ec4899",
    description: "Wholesale and retail trade"
  },
  "EMP. ADM. PART. - COMÉRCIO (ATACADO E VAREJO)": {
    shortName: "Retail",
    icon: "🛒",
    color: "#ec4899",
    description: "Retail holding companies"
  },
  "ALIMENTOS": {
    shortName: "Food",
    icon: "🍽️",
    color: "#22c55e",
    description: "Food products"
  },
  "EMP. ADM. PART. - ALIMENTOS": {
    shortName: "Food",
    icon: "🍽️",
    color: "#22c55e",
    description: "Food holding companies"
  },
  "BEBIDAS E FUMO": {
    shortName: "Beverages",
    icon: "🥤",
    color: "#f97316",
    description: "Beverages and tobacco"
  },
  "AGRICULTURA (AÇÚCAR, ÁLCOOL E CANA)": {
    shortName: "Agro",
    icon: "🌾",
    color: "#65a30d",
    description: "Sugar, alcohol and sugarcane"
  },
  "FARMACÊUTICO E HIGIENE": {
    shortName: "Pharma",
    icon: "💊",
    color: "#10b981",
    description: "Pharmaceutical and hygiene"
  },

  // Technology & Communications
  "TELECOMUNICAÇÕES": {
    shortName: "Telecom",
    icon: "📱",
    color: "#6366f1",
    description: "Telecommunications"
  },
  "COMUNICAÇÃO E INFORMÁTICA": {
    shortName: "IT",
    icon: "💻",
    color: "#8b5cf6",
    description: "Communication and IT"
  },

  // Industrial & Manufacturing
  "MÁQUINAS, EQUIPAMENTOS, VEÍCULOS E PEÇAS": {
    shortName: "Machinery",
    icon: "⚙️",
    color: "#475569",
    description: "Machinery, equipment and vehicles"
  },
  "EMP. ADM. PART. - MÁQS., EQUIP., VEÍC. E PEÇAS": {
    shortName: "Machinery",
    icon: "⚙️",
    color: "#475569",
    description: "Machinery holding companies"
  },
  "CONSTRUÇÃO CIVIL, MAT. CONSTR. E DECORAÇÃO": {
    shortName: "Construction",
    icon: "🏗️",
    color: "#ea580c",
    description: "Civil construction and materials"
  },
  "EMP. ADM. PART. - CONST. CIVIL, MAT. CONST. E DECORAÇÃO": {
    shortName: "Construction",
    icon: "🏗️",
    color: "#ea580c",
    description: "Construction holding companies"
  },
  "TÊXTIL E VESTUÁRIO": {
    shortName: "Textile",
    icon: "👕",
    color: "#d946ef",
    description: "Textile and clothing"
  },

  // Services
  "SERVIÇOS TRANSPORTE E LOGÍSTICA": {
    shortName: "Logistics",
    icon: "🚛",
    color: "#0891b2",
    description: "Transport and logistics services"
  },
  "EMP. ADM. PART. - SERVIÇOS TRANSPORTE E LOGÍSTICA": {
    shortName: "Logistics",
    icon: "🚛",
    color: "#0891b2",
    description: "Logistics holding companies"
  },
  "HOSPEDAGEM E TURISMO": {
    shortName: "Tourism",
    icon: "🏨",
    color: "#06b6d4",
    description: "Hospitality and tourism"
  },
  "SERVIÇOS MÉDICOS": {
    shortName: "Healthcare",
    icon: "🏥",
    color: "#ef4444",
    description: "Medical services"
  },
  "EMP. ADM. PART. - EDUCAÇÃO": {
    shortName: "Education",
    icon: "🎓",
    color: "#3b82f6",
    description: "Education services"
  },

  // Other/Miscellaneous
  "EMP. ADM. PART. - SEM SETOR PRINCIPAL": {
    shortName: "Holding",
    icon: "🏢",
    color: "#64748b",
    description: "Holding companies without main sector"
  }
};

/**
 * Get sector mapping for a given sector name
 * Returns a default mapping if sector is not found
 */
export const getSectorMapping = (sectorName: string | null | undefined): SectorMapping => {
  if (!sectorName) {
    return {
      shortName: "Other",
      icon: "❓",
      color: "#9ca3af",
      description: "Uncategorized"
    };
  }

  const mapping = SECTOR_MAPPINGS[sectorName];
  if (mapping) {
    return mapping;
  }

  // Return default for unknown sectors
  return {
    shortName: "Other",
    icon: "❓",
    color: "#9ca3af",
    description: sectorName
  };
};

/**
 * Get short name for a sector
 */
export const getSectorShortName = (sectorName: string | null | undefined): string => {
  return getSectorMapping(sectorName).shortName;
};

/**
 * Get icon for a sector
 */
export const getSectorIcon = (sectorName: string | null | undefined): string => {
  return getSectorMapping(sectorName).icon;
};

/**
 * Get color for a sector
 */
export const getSectorColor = (sectorName: string | null | undefined): string => {
  return getSectorMapping(sectorName).color;
};

/**
 * Get all unique sector mappings (for legend/reference)
 */
export const getAllSectorMappings = (): Array<{ originalName: string; mapping: SectorMapping }> => {
  return Object.entries(SECTOR_MAPPINGS).map(([originalName, mapping]) => ({
    originalName,
    mapping
  }));
};
