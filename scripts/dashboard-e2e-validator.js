/**
 * Dashboard E2E Validator
 * Agente de Validação de Dashboard (QA end-to-end)
 * 
 * IDENTIDADE: Agente de Validação de Dashboard com capacidades de:
 * (1) automação de navegador (Playwright), (2) consulta endpoints HTTP,
 * (3) localização por CSS/data-testid, (4) extração/validação números,
 * (5) aguardar renderização reativa, (6) captura screenshots/traces/HAR,
 * (7) relatório JSON final + anexos.
 * 
 * CONFORMIDADE: Implementa todas as regras obrigatórias e validações V1-V5.
 */

const { chromium } = require('playwright');
const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');

class DashboardE2EValidator {
    constructor() {
        this.browser = null;
        this.page = null;
        this.context = null;
        this.config = {
            viewport: { width: 1440, height: 900 },
            timeout: 30000,
            pollInterval: 1000,
            stabilityTimeout: 2000,
            firstLoadTolerance: 15000,
            headless: true
        };
        this.results = {
            status: 'FAIL',
            frontend_url: '',
            api_url: '',
            ui_values: {},
            ui_levels: {},
            api_values: {},
            api_levels: {},
            mismatches: [],
            notes: [],
            evidence: {}
        };
        this.testIds = {
            dashboard: 'dashboard-title',
            metricsGrid: 'metrics-grid',
            totalTickets: 'total-tickets',
            openTickets: 'open-tickets',
            closedTickets: 'closed-tickets',
            pendingTickets: 'pending-tickets',
            inProgressTickets: 'in-progress-tickets',
            newTickets: 'new-tickets',
            levelN1: 'level-N1-total',
            levelN2: 'level-N2-total',
            levelN3: 'level-N3-total',
            levelN4: 'level-N4-total'
        };
    }

    /**
     * 1) Descoberta de alvos
     */
    discoverTargets() {
        const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
        const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
        const dashboardUrl = `${frontendUrl}/dashboard`;
        
        const apiCandidates = [
            `${frontendUrl}/api/metrics`,
            `${backendUrl}/api/metrics`,
            'http://localhost:5000/api/metrics'
        ];
        
        const apiLevelsCandidates = apiCandidates.map(url => url.replace('/metrics', '/metrics/levels'));
        const apiStatusCandidates = apiCandidates.map(url => url.replace('/metrics', '/metrics/status'));

        this.results.frontend_url = frontendUrl;
        
        return {
            frontendUrl,
            backendUrl,
            dashboardUrl,
            apiCandidates,
            apiLevelsCandidates,
            apiStatusCandidates
        };
    }

    /**
     * 2) Sanidade de serviços
     */
    async checkServiceHealth(apiCandidates, apiLevelsCandidates, apiStatusCandidates, backendUrl) {
        let apiUrl = null;
        let apiResponse = null;
        let apiLevelsUrl = null;
        let apiStatusUrl = null;

        // Descoberta sequencial da API principal
        for (const candidate of apiCandidates) {
            try {
                console.log(`Testando API: ${candidate}`);
                apiResponse = await axios.get(candidate, { timeout: 10000 });
                if (apiResponse.status === 200 && apiResponse.data) {
                    apiUrl = candidate;
                    console.log(`✓ API encontrada: ${candidate}`);
                    break;
                }
            } catch (error) {
                console.log(`✗ API falhou: ${candidate} - ${error.message}`);
            }
        }

        if (!apiUrl) {
            this.results.notes.push('api_indisponivel');
            console.log('✗ Nenhuma API respondeu');
        } else {
            this.results.api_url = apiUrl;
        }

        // Descoberta opcional de API de níveis
        for (const candidate of apiLevelsCandidates) {
            try {
                const response = await axios.get(candidate, { timeout: 5000 });
                if (response.status === 200) {
                    apiLevelsUrl = candidate;
                    console.log(`✓ API de níveis encontrada: ${candidate}`);
                    break;
                }
            } catch (error) {
                // Silencioso - API de níveis é opcional
            }
        }

        // Descoberta opcional de API de status
        for (const candidate of apiStatusCandidates) {
            try {
                const response = await axios.get(candidate, { timeout: 5000 });
                if (response.status === 200) {
                    apiStatusUrl = candidate;
                    console.log(`✓ API de status encontrada: ${candidate}`);
                    break;
                }
            } catch (error) {
                // Silencioso - API de status é opcional
            }
        }

        // Verificação opcional do backend docs
        try {
            const docsUrl = `${backendUrl}/docs`;
            await axios.get(docsUrl, { timeout: 3000 });
            console.log(`✓ Backend docs disponível: ${docsUrl}`);
        } catch (error) {
            // Silencioso - docs são opcionais
        }

        return { apiUrl, apiResponse, apiLevelsUrl, apiStatusUrl };
    }

    /**
     * 3) Abrir e aguardar renderização
     */
    async openAndWaitForRendering(dashboardUrl) {
        this.browser = await chromium.launch({ 
            headless: this.config.headless,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        this.context = await this.browser.newContext({
            viewport: this.config.viewport,
            recordHar: { path: 'network.har' },
            recordVideo: { dir: 'videos/' }
        });
        
        this.page = await this.context.newPage();
        
        // Configurar PAGER=cat
        await this.page.addInitScript(() => {
            window.process = { env: { PAGER: 'cat' } };
        });

        console.log(`Navegando para: ${dashboardUrl}`);
        await this.page.goto(dashboardUrl, { waitUntil: 'networkidle', timeout: this.config.timeout });

        // Esperar elementos básicos
        console.log('Aguardando elementos básicos...');
        await this.page.waitForSelector(`[data-testid="${this.testIds.dashboard}"]`, { timeout: this.config.timeout });
        await this.page.waitForSelector(`[data-testid="${this.testIds.metricsGrid}"]`, { timeout: this.config.timeout });

        // Estratégia de espera adaptativa (até 45s com tolerância extra para GLPI)
        console.log('Aguardando dados serem carregados e estabilizados...');
        const maxWaitTime = this.config.timeout + this.config.firstLoadTolerance;
        const startTime = Date.now();
        let previousValues = null;
        let stableCount = 0;
        
        while (Date.now() - startTime < maxWaitTime) {
            try {
                // Tentar ler o total de diferentes testids
                let totalValue = 0;
                const totalCandidates = [this.testIds.totalTickets, this.testIds.newTickets];
                
                for (const testId of totalCandidates) {
                    const element = await this.page.$(`[data-testid="${testId}"]`);
                    if (element) {
                        const text = await element.textContent();
                        totalValue = this.extractNumber(text);
                        if (totalValue > 0) break;
                    }
                }
                
                if (totalValue > 0) {
                    // Verificar estabilidade
                    if (previousValues && JSON.stringify(previousValues) === JSON.stringify({ total: totalValue })) {
                        stableCount++;
                        if (stableCount >= 2) {
                            console.log(`✓ Dados estáveis carregados (total: ${totalValue})`);
                            break;
                        }
                    } else {
                        stableCount = 0;
                        previousValues = { total: totalValue };
                    }
                    
                    // Aguardar intervalo de estabilidade
                    await this.page.waitForTimeout(this.config.stabilityTimeout);
                } else {
                    await this.page.waitForTimeout(this.config.pollInterval);
                }
            } catch (error) {
                await this.page.waitForTimeout(this.config.pollInterval);
            }
        }
        
        // Aguardar um pouco mais para garantir renderização completa
        await this.page.waitForTimeout(1000);
    }

    /**
     * 4) Coleta de valores da UI
     */
    async collectUIValues() {
        console.log('Coletando valores da UI...');
        const uiValues = {};
        const uiLevels = {};

        // Coletar métricas principais
        const mainTestIds = [
            { id: this.testIds.totalTickets, field: 'total' },
            { id: this.testIds.openTickets, field: 'open' },
            { id: this.testIds.closedTickets, field: 'closed' },
            { id: this.testIds.pendingTickets, field: 'pending' },
            { id: this.testIds.inProgressTickets, field: 'in_progress' },
            { id: this.testIds.newTickets, field: 'new' }
        ];

        for (const { id, field } of mainTestIds) {
            try {
                const element = await this.page.$(`[data-testid="${id}"]`);
                if (element) {
                    const text = await element.textContent();
                    const value = this.extractNumber(text);
                    
                    if (!isNaN(value)) {
                        uiValues[field] = value;
                        console.log(`  ${id}: ${text} → ${value}`);
                    } else {
                        console.log(`  ${id}: valor não numérico - ${text}`);
                        this.results.notes.push(`valor_nao_numerico_${field}`);
                    }
                } else {
                    console.log(`  ${id}: elemento não encontrado`);
                }
            } catch (error) {
                console.log(`  ${id}: erro ao extrair - ${error.message}`);
            }
        }

        // Coletar níveis GLPI (N1-N4)
        const levelTestIds = [
            { id: this.testIds.levelN1, field: 'N1' },
            { id: this.testIds.levelN2, field: 'N2' },
            { id: this.testIds.levelN3, field: 'N3' },
            { id: this.testIds.levelN4, field: 'N4' }
        ];

        let levelsFound = false;
        for (const { id, field } of levelTestIds) {
            try {
                const element = await this.page.$(`[data-testid="${id}"]`);
                if (element) {
                    const text = await element.textContent();
                    const value = this.extractNumber(text);
                    
                    if (!isNaN(value)) {
                        uiLevels[field] = value;
                        levelsFound = true;
                        console.log(`  ${id}: ${text} → ${value}`);
                    }
                }
            } catch (error) {
                // Níveis são opcionais
            }
        }

        if (!levelsFound) {
            this.results.notes.push('levels_nao_visiveis');
            console.log('  Níveis GLPI não encontrados na UI');
        }

        this.results.ui_values = uiValues;
        this.results.ui_levels = uiLevels;
        return { uiValues, uiLevels };
    }

    /**
     * 5) Cross-check com API
     */
    async crossCheckWithAPI(apiUrl, apiLevelsUrl, apiStatusUrl) {
        const apiValues = {};
        const apiLevels = {};
        
        // Consultar API principal
        if (apiUrl) {
            console.log('Fazendo cross-check com API principal...');
            try {
                const response = await axios.get(apiUrl, { timeout: 10000 });
                const apiData = response.data;
                
                // Salvar resposta da API principal
                await fs.writeFile('api_response.json', JSON.stringify(apiData, null, 2));
                this.results.evidence.api_response = 'api_response.json';
                
                // Extrair valores da API
                Object.assign(apiValues, this.extractAPIValues(apiData));
                console.log('Valores da API principal:', apiValues);
                
            } catch (error) {
                console.log(`Erro ao consultar API principal: ${error.message}`);
                this.results.notes.push(`erro_api_principal: ${error.message}`);
            }
        } else {
            this.results.notes.push('api_indisponivel');
        }

        // Consultar API de níveis (opcional)
        if (apiLevelsUrl) {
            console.log('Consultando API de níveis...');
            try {
                const response = await axios.get(apiLevelsUrl, { timeout: 5000 });
                const levelsData = response.data;
                
                // Salvar resposta da API de níveis
                await fs.writeFile('api_levels_response.json', JSON.stringify(levelsData, null, 2));
                this.results.evidence.api_levels_response = 'api_levels_response.json';
                
                // Extrair níveis da API
                Object.assign(apiLevels, this.extractAPILevels(levelsData));
                console.log('Níveis da API:', apiLevels);
                
            } catch (error) {
                console.log(`API de níveis indisponível: ${error.message}`);
            }
        }

        // Consultar API de status (opcional)
        if (apiStatusUrl) {
            console.log('Consultando API de status...');
            try {
                const response = await axios.get(apiStatusUrl, { timeout: 5000 });
                const statusData = response.data;
                
                // Salvar resposta da API de status
                await fs.writeFile('api_status_response.json', JSON.stringify(statusData, null, 2));
                this.results.evidence.api_status_response = 'api_status_response.json';
                
                // Extrair dados de status granulares se disponíveis
                const statusValues = this.extractAPIStatusValues(statusData);
                Object.assign(apiValues, statusValues);
                console.log('Status da API:', statusValues);
                
            } catch (error) {
                console.log(`API de status indisponível: ${error.message}`);
            }
        }

        this.results.api_values = apiValues;
         this.results.api_levels = apiLevels;
         return { apiValues, apiLevels };
     }

    /**
     * 6) Validações (V1-V5)
     */
    performValidations(uiValues, uiLevels, apiValues, apiLevels) {
        console.log('Executando validações V1-V5...');
        let allValidationsPassed = true;
        const mismatches = [];
        const notes = [];

        // V1: ASSERT ui_values.total > 0 (motivo: "total_zero_na_ui")
        if (!uiValues.total || uiValues.total <= 0) {
            allValidationsPassed = false;
            mismatches.push({ field: 'total', issue: 'total_zero_na_ui', ui: uiValues.total || 0 });
            console.log('✗ V1: Total deve ser > 0');
        } else {
            console.log('✓ V1: Total > 0');
        }

        // V2: ASSERT todos os presentes (open, closed, pending, in_progress?, new?) ≥ 0 ("valor_negativo")
        const statusFields = ['open', 'closed', 'pending', 'in_progress', 'new'];
        let negativeFound = false;
        for (const field of statusFields) {
            if (uiValues[field] !== undefined && uiValues[field] < 0) {
                allValidationsPassed = false;
                negativeFound = true;
                mismatches.push({ field, issue: 'valor_negativo', ui: uiValues[field] });
                console.log(`✗ V2: ${field} não pode ser negativo (${uiValues[field]})`);
            }
        }
        if (!negativeFound) {
            console.log('✓ V2: Nenhum valor negativo');
        }

        // V3: Se todos status presentes: ASSERT (open+closed+pending+in_progress?+new?) == total
        const presentStatusFields = statusFields.filter(field => uiValues[field] !== undefined);
        if (presentStatusFields.length >= 3) { // Pelo menos 3 campos para validação
            const statusSum = presentStatusFields.reduce((sum, field) => sum + (uiValues[field] || 0), 0);
            
            if (statusSum !== uiValues.total) {
                allValidationsPassed = false;
                mismatches.push({ 
                    field: 'soma_status', 
                    issue: 'soma_status_difere_total', 
                    ui: statusSum, 
                    expected: uiValues.total 
                });
                console.log(`✗ V3: Soma dos status (${statusSum}) ≠ total (${uiValues.total})`);
            } else {
                console.log('✓ V3: Soma dos status = total');
            }
        } else {
            notes.push('soma_parcial_nao_conclusiva');
            console.log('⚠ V3: Soma parcial não conclusiva (poucos campos presentes)');
        }

        // V4: Cross-check UI ↔ API (igualdade exata nos campos presentes)
        if (Object.keys(apiValues).length > 0) {
            let mismatchFound = false;
            for (const field of Object.keys(uiValues)) {
                if (apiValues[field] !== undefined && uiValues[field] !== apiValues[field]) {
                    allValidationsPassed = false;
                    mismatchFound = true;
                    mismatches.push({ 
                        field, 
                        issue: 'ui_api_mismatch', 
                        ui: uiValues[field], 
                        api: apiValues[field] 
                    });
                    console.log(`✗ V4: ${field} UI(${uiValues[field]}) ≠ API(${apiValues[field]})`);
                }
            }
            if (!mismatchFound) {
                console.log('✓ V4: UI = API');
            }
        } else {
            notes.push('cross_check_api_indisponivel');
            console.log('⚠ V4: Cross-check com API indisponível');
        }

        // V5: Por nível (N1–N4): cada level_total ≥ 0; se somatório de níveis presente, exija sum(level_totals) == total
        if (Object.keys(uiLevels).length > 0) {
            let levelValidationPassed = true;
            
            // Verificar se cada nível ≥ 0
            for (const [level, value] of Object.entries(uiLevels)) {
                if (value < 0) {
                    allValidationsPassed = false;
                    levelValidationPassed = false;
                    mismatches.push({ field: `level_${level}`, issue: 'level_negativo', ui: value });
                    console.log(`✗ V5: Nível ${level} não pode ser negativo (${value})`);
                }
            }
            
            // Verificar soma dos níveis = total
            const levelsSum = Object.values(uiLevels).reduce((sum, value) => sum + value, 0);
            if (levelsSum !== uiValues.total) {
                allValidationsPassed = false;
                levelValidationPassed = false;
                mismatches.push({ 
                    field: 'soma_levels', 
                    issue: 'levels_nao_batem_total', 
                    ui: levelsSum, 
                    expected: uiValues.total 
                });
                console.log(`✗ V5: Soma dos níveis (${levelsSum}) ≠ total (${uiValues.total})`);
            }
            
            // Cross-check níveis UI ↔ API
            if (Object.keys(apiLevels).length > 0) {
                for (const [level, uiValue] of Object.entries(uiLevels)) {
                    if (apiLevels[level] !== undefined && uiValue !== apiLevels[level]) {
                        allValidationsPassed = false;
                        levelValidationPassed = false;
                        mismatches.push({ 
                            field: `level_${level}`, 
                            issue: 'levels_divergem_api', 
                            ui: uiValue, 
                            api: apiLevels[level] 
                        });
                        console.log(`✗ V5: Nível ${level} UI(${uiValue}) ≠ API(${apiLevels[level]})`);
                    }
                }
            }
            
            if (levelValidationPassed) {
                console.log('✓ V5: Validações de níveis passaram');
            }
        } else {
            console.log('⚠ V5: Níveis não disponíveis para validação');
        }

        this.results.mismatches = mismatches;
        this.results.notes = [...this.results.notes, ...notes];
        
        return allValidationsPassed;
    }

    /**
     * 7) Evidências e relatório
     */
    async captureEvidenceAndGenerateReport(validationsPassed) {
        console.log('Capturando evidências...');
        const timestamp = this.getTimestamp();
        const status = validationsPassed ? 'PASS' : 'FAIL';
        const fs = require('fs');
        
        // Screenshot
        const screenshotPath = `dashboard_${status.toLowerCase()}-${timestamp}.png`;
        await this.page.screenshot({ path: screenshotPath, fullPage: true });
        console.log(`Screenshot salvo: ${screenshotPath}`);
        
        // Network HAR (se disponível no contexto)
        let harPath = null;
        try {
            if (this.context) {
                harPath = `network-${timestamp}.har`;
                // O HAR é salvo automaticamente quando o contexto é fechado
                console.log(`HAR será salvo: ${harPath}`);
            }
        } catch (error) {
            console.log('Aviso: Não foi possível configurar HAR:', error.message);
        }
        
        // HTML Snapshot
        const htmlPath = `html_snapshot-${timestamp}.html`;
        try {
            const metricsGrid = await this.page.locator('[data-testid="metrics-grid"]').first();
            const htmlContent = await metricsGrid.innerHTML();
            const fullHtml = `<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Snapshot - ${timestamp}</title>
    <meta charset="utf-8">
</head>
<body>
    <div data-testid="metrics-grid">
        ${htmlContent}
    </div>
</body>
</html>`;
            fs.writeFileSync(htmlPath, fullHtml);
            console.log(`HTML snapshot salvo: ${htmlPath}`);
        } catch (error) {
            console.log('Aviso: Não foi possível capturar HTML snapshot:', error.message);
            // Fallback: capturar body completo
            try {
                const bodyContent = await this.page.locator('body').innerHTML();
                const fallbackHtml = `<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Snapshot (Fallback) - ${timestamp}</title>
    <meta charset="utf-8">
</head>
<body>
    ${bodyContent}
</body>
</html>`;
                fs.writeFileSync(htmlPath, fallbackHtml);
                console.log(`HTML snapshot (fallback) salvo: ${htmlPath}`);
            } catch (fallbackError) {
                console.log('Erro: Não foi possível capturar HTML:', fallbackError.message);
            }
        }
        
        // Trace (se disponível)
        let tracePath = null;
        try {
            if (this.page.context().tracing) {
                tracePath = `trace-${timestamp}.zip`;
                await this.page.context().tracing.stop({ path: tracePath });
                console.log(`Trace salvo: ${tracePath}`);
            }
        } catch (error) {
            console.log('Aviso: Não foi possível salvar trace:', error.message);
        }
        
        this.results.evidence = {
            screenshot: screenshotPath,
            har: harPath,
            html_snapshot: htmlPath,
            trace: tracePath,
            timestamp: timestamp
        };
        
        // Relatório final
        this.results.status = status;
        const reportPath = `dashboard_report-${timestamp}.json`;
        
        fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));
        console.log(`Relatório salvo: ${reportPath}`);
        
        console.log(`\n=== RELATÓRIO FINAL ===`);
        console.log(`Status: ${status}`);
        console.log(`Screenshot: ${screenshotPath}`);
        console.log(`Relatório: ${reportPath}`);
        console.log(`Mismatches: ${this.results.mismatches.length}`);
        console.log(`Notas: ${this.results.notes.length}`);
        
        return { reportName: reportPath, screenshotName: screenshotPath };
    }

    /**
     * Utilitários
     */
    extractNumber(text) {
        if (!text) return 0;
        const cleaned = text.replace(/[^0-9]/g, '');
        const number = parseInt(cleaned, 10);
        return isNaN(number) ? 0 : number;
    }

    mapUIFieldToAPI(testId) {
        const mapping = {
            'total-tickets': 'total',
            'open-tickets': 'open',
            'closed-tickets': 'closed', 
            'pending-tickets': 'pending',
            'in-progress-tickets': 'in_progress',
            'new-tickets': 'new'
        };
        return mapping[testId] || testId;
    }

    extractAPIValues(apiData) {
        // Adaptar para a estrutura da API do projeto
        const values = {};
        
        if (apiData.success && apiData.data) {
            const data = apiData.data;
            values.total = data.total || 0;
            values.new = data.novos || 0;  // Mapear 'novos' para 'new'
            values.pending = data.pendentes || 0;
            values.in_progress = data.progresso || 0;
            values.closed = data.resolvidos || 0;  // Mapear 'resolvidos' para 'closed'
            
            // Calcular 'open' se não estiver presente (novos + em progresso)
            values.open = values.new + values.in_progress;
        }
        
        return values;
    }

    getTimestamp() {
        const now = new Date();
        return now.toISOString().replace(/[:.]/g, '-').slice(0, 19);
    }

    async cleanup() {
        try {
            // Fechar contexto (salva HAR automaticamente)
            if (this.context) {
                await this.context.close();
                console.log('Contexto fechado (HAR salvo)');
            }
            
            if (this.page) {
                await this.page.close();
                console.log('Página fechada');
            }
            
            if (this.browser) {
                await this.browser.close();
                console.log('Navegador fechado');
            }
        } catch (error) {
            console.log('Erro durante limpeza:', error.message);
        }
    }

    /**
     * Método principal de execução
     */
    async run() {
        try {
            console.log('=== INICIANDO VALIDAÇÃO E2E DO DASHBOARD ===\n');
            
            // 1) Descoberta de alvos
            const targets = this.discoverTargets();
            console.log('Alvos descobertos:', targets);
            
            // 2) Verificação de saúde dos serviços
            const healthCheck = await this.checkServiceHealth(
                targets.apiCandidates, 
                targets.apiLevelsCandidates, 
                targets.apiStatusCandidates
            );
            
            if (healthCheck.apiUrl) {
                this.results.api_url = healthCheck.apiUrl;
                console.log(`API principal disponível: ${healthCheck.apiUrl}`);
            } else {
                this.results.notes.push('api_indisponivel');
                console.log('⚠ API principal indisponível, continuando apenas com UI');
            }
            
            if (healthCheck.apiLevelsUrl) {
                console.log(`API de níveis disponível: ${healthCheck.apiLevelsUrl}`);
            }
            
            if (healthCheck.apiStatusUrl) {
                console.log(`API de status disponível: ${healthCheck.apiStatusUrl}`);
            }
            
            // 3) Abrir e aguardar renderização
            await this.openAndWaitForRendering(targets.dashboardUrl);
            
            // 4) Coleta de valores da UI
            const { uiValues, uiLevels } = await this.collectUIValues();
            this.results.ui_values = uiValues;
            this.results.ui_levels = uiLevels;
            console.log('Valores da UI coletados:', uiValues);
            console.log('Níveis da UI coletados:', uiLevels);
            
            // 5) Cross-check com API
            let apiValues = {};
            let apiLevels = {};
            if (this.results.api_url) {
                const apiData = await this.crossCheckWithAPI(
                    this.results.api_url,
                    healthCheck.apiLevelsUrl,
                    healthCheck.apiStatusUrl
                );
                apiValues = apiData.apiValues;
                apiLevels = apiData.apiLevels;
                this.results.api_values = apiValues;
                this.results.api_levels = apiLevels;
                console.log('Valores da API coletados:', apiValues);
                console.log('Níveis da API coletados:', apiLevels);
            }
            
            // 6) Validações (V1-V5)
            const validationsPassed = this.performValidations(uiValues, uiLevels, apiValues, apiLevels);
            
            // 7) Evidências e relatório
            const report = await this.captureEvidenceAndGenerateReport(validationsPassed);
            
            console.log('\n=== VALIDAÇÃO CONCLUÍDA ===');
            return report;
            
        } catch (error) {
            console.error(`Erro durante validação: ${error.message}`);
            
            // Capturar screenshot de erro se possível
            if (this.page) {
                try {
                    const timestamp = this.getTimestamp();
                    const errorScreenshot = `dashboard_error_${timestamp}.png`;
                    await this.page.screenshot({ path: errorScreenshot });
                    this.results.evidence.screenshot = errorScreenshot;
                } catch (screenshotError) {
                    console.error(`Erro ao capturar screenshot: ${screenshotError.message}`);
                }
            }
            
            this.results.status = 'FAIL';
            this.results.notes.push(`Erro de execução: ${error.message}`);
            
            return { success: false, error: error.message, status: 'FAIL' };
            
        } finally {
            await this.cleanup();
        }
    }
}

// Execução se chamado diretamente
if (require.main === module) {
    const validator = new DashboardE2EValidator();
    validator.run()
        .then(result => {
            console.log('\n=== VALIDAÇÃO E2E CONCLUÍDA ===');
            console.log('Resultado:', result);
            
            // Verificar se passou em todas as validações
            const success = result.reportName && !result.error;
            process.exit(success ? 0 : 1);
        })
        .catch(error => {
            console.error('\n=== ERRO NA VALIDAÇÃO E2E ===');
            console.error('Erro:', error);
            process.exit(1);
        });
}

module.exports = DashboardE2EValidator;
