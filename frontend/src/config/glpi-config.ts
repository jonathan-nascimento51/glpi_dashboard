// Configuração baseada nos dados reais do GLPI
// Adaptado para o cenário de poucos dados iniciais

export const GLPI_CONFIG = {
  // Categorias principais baseadas nos dados reais
  MAIN_CATEGORIES: {
    'Manutenção': {
      icon: 'Wrench',
      color: 'blue',
      subcategories: [
        'Hidráulica',
        'Elétrica', 
        'Ar Condicionado',
        'Rede Computadores',
        'Marcenaria'
      ]
    },
    'Conservação': {
      icon: 'Shield',
      color: 'green',
      subcategories: [
        'Limpeza',
        'Jardinagem',
        'Copa',
        'Carregadores',
        'Mensageria'
      ]
    }
  },

  // Categorias com dados reais nos últimos 7 dias
  ACTIVE_CATEGORIES: [
    'Manutenção > Hidráulica > Desentupimento',
    'Manutenção > Rede Computadores > Readequação Rede Lógica'
  ],

  // Mensagens adaptadas para poucos dados
  MESSAGES: {
    EMPTY_STATE: {
      title: 'Sistema GLPI Recém Implementado',
      description: 'Aguardando mais solicitações para gerar estatísticas completas',
      categories_available: 'Categorias disponíveis: Manutenção e Conservação'
    },
    LOW_DATA: {
      title: 'Poucas categorias com dados',
      description: 'O sistema foi implementado recentemente. Dados disponíveis:',
      wait_message: 'Aguarde mais solicitações para visualizar estatísticas'
    }
  },

  // Configurações de exibição
  DISPLAY: {
    MAX_CATEGORIES: 100,
    MIN_TICKETS_FOR_TREND: 5,
    REFRESH_INTERVAL: 300000, // 5 minutos
    SHOW_EMPTY_CATEGORIES: true
  },

  // Mapeamento de status do GLPI
  STATUS_MAPPING: {
    'Novo': { color: 'blue', label: 'Novos' },
    'Processando (atribuído)': { color: 'yellow', label: 'Em Execução' },
    'Processando (planejado)': { color: 'yellow', label: 'Em Execução' },
    'Pendente': { color: 'orange', label: 'Aguardando' },
    'Solucionado': { color: 'green', label: 'Concluídos' },
    'Fechado': { color: 'green', label: 'Concluídos' }
  },

  // Configurações de performance
  PERFORMANCE: {
    CACHE_TTL: 180, // 3 minutos
    MAX_RETRIES: 3,
    TIMEOUT: 10000 // 10 segundos
  }
};

// Função para obter configuração de categoria
export const getCategoryConfig = (categoryName: string) => {
  const mainCategory = Object.keys(GLPI_CONFIG.MAIN_CATEGORIES).find(cat => 
    categoryName.startsWith(cat)
  );
  
  return mainCategory ? GLPI_CONFIG.MAIN_CATEGORIES[mainCategory as keyof typeof GLPI_CONFIG.MAIN_CATEGORIES] : null;
};

// Função para verificar se categoria tem dados
export const hasActiveData = (categoryName: string) => {
  return GLPI_CONFIG.ACTIVE_CATEGORIES.some(active => 
    active.includes(categoryName) || categoryName.includes(active)
  );
};

// Função para formatar mensagens baseadas no contexto
export const getContextualMessage = (dataCount: number) => {
  if (dataCount === 0) {
    return GLPI_CONFIG.MESSAGES.EMPTY_STATE;
  } else if (dataCount < 5) {
    return GLPI_CONFIG.MESSAGES.LOW_DATA;
  }
  return null;
};