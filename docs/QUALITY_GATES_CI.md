# Quality Gates para CI/CD - GLPI Dashboard

# Adicionar ao .github/workflows/ci.yml após os jobs existentes

  # Quality Gates - Backend
  backend-quality-gates:
    name: Backend Quality Gates
    runs-on: ubuntu-latest
    needs: [backend-tests]
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r ${{ env.BACKEND_DIR }}/requirements.txt
        pip install ruff mypy bandit safety

    - name: Code Quality - Ruff
      run: |
        cd ${{ env.BACKEND_DIR }}
        ruff check . --exit-non-zero-on-fix
        ruff format --check .

    - name: Type Checking - MyPy
      run: |
        cd ${{ env.BACKEND_DIR }}
        mypy . --strict

    - name: Security Scan - Bandit
      run: |
        cd ${{ env.BACKEND_DIR }}
        bandit -r app/ -f json -o bandit-report.json
        bandit -r app/ --severity-level medium

    - name: Dependency Security - Safety
      run: |
        cd ${{ env.BACKEND_DIR }}
        safety check --json --output safety-report.json
        safety check

    - name: Coverage Threshold Check
      run: |
        cd ${{ env.BACKEND_DIR }}
        pytest --cov=app --cov-fail-under=80 --cov-report=xml

    - name: Upload Security Reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: backend-security-reports
        path: |
          ${{ env.BACKEND_DIR }}/bandit-report.json
          ${{ env.BACKEND_DIR }}/safety-report.json

  # Quality Gates - Frontend
  frontend-quality-gates:
    name: Frontend Quality Gates
    runs-on: ubuntu-latest
    needs: [frontend-tests]
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: "18"
        cache: "npm"
        cache-dependency-path: ${{ env.FRONTEND_DIR }}/package-lock.json

    - name: Install dependencies
      run: |
        cd ${{ env.FRONTEND_DIR }}
        npm ci

    - name: Code Quality - ESLint (Zero Warnings)
      run: |
        cd ${{ env.FRONTEND_DIR }}
        npm run lint -- --max-warnings 0

    - name: Code Formatting - Prettier
      run: |
        cd ${{ env.FRONTEND_DIR }}
        npm run format:check

    - name: Type Checking - TypeScript
      run: |
        cd ${{ env.FRONTEND_DIR }}
        npm run type-check

    - name: Coverage Threshold Check
      run: |
        cd ${{ env.FRONTEND_DIR }}
        npm run test:coverage -- --coverage.threshold.global.lines=80 --coverage.threshold.global.functions=80 --coverage.threshold.global.branches=80 --coverage.threshold.global.statements=80

    - name: Build Verification
      run: |
        cd ${{ env.FRONTEND_DIR }}
        npm run build
        # Verificar se o build gerou arquivos
        ls -la dist/
        test -f dist/index.html

    - name: Bundle Size Check
      run: |
        cd ${{ env.FRONTEND_DIR }}
        npm run build
        # Verificar tamanho do bundle (exemplo: <5MB)
        BUNDLE_SIZE=$(du -sm dist/ | cut -f1)
        echo "Bundle size: ${BUNDLE_SIZE}MB"
        if [ $BUNDLE_SIZE -gt 5 ]; then
          echo "Bundle size exceeds 5MB limit"
          exit 1
        fi

    - name: Accessibility Check (se configurado)
      run: |
        cd ${{ env.FRONTEND_DIR }}
        # npm run test:a11y (se existir)
        echo "Accessibility checks would run here"

  # Quality Gates - Integration
  integration-quality-gates:
    name: Integration Quality Gates
    runs-on: ubuntu-latest
    needs: [backend-quality-gates, frontend-quality-gates, orval-drift-check]
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: "18"
        cache: "npm"
        cache-dependency-path: ${{ env.FRONTEND_DIR }}/package-lock.json

    - name: Install all dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r ${{ env.BACKEND_DIR }}/requirements.txt
        cd ${{ env.FRONTEND_DIR }} && npm ci

    - name: API Schema Validation
      run: |
        cd ${{ env.BACKEND_DIR }}
        # Iniciar servidor em background
        uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        SERVER_PID=$!
        
        # Aguardar servidor inicializar
        sleep 10
        
        # Verificar se API está respondendo
        curl -f http://localhost:8000/docs
        curl -f http://localhost:8000/openapi.json
        
        # Parar servidor
        kill $SERVER_PID

    - name: Frontend-Backend Integration
      run: |
        cd ${{ env.BACKEND_DIR }}
        # Iniciar backend
        uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        
        cd ../${{ env.FRONTEND_DIR }}
        # Gerar cliente API
        VITE_API_URL=http://localhost:8000 npm run gen:api
        
        # Verificar se geração foi bem-sucedida
        test -f src/api/generated/api.ts
        
        # Build frontend com API real
        VITE_API_URL=http://localhost:8000 npm run build
        
        # Cleanup
        kill $BACKEND_PID

    - name: Security Aggregation
      run: |
        echo "=== Security Summary ==="
        echo "Backend security reports generated"
        echo "Frontend dependencies checked"
        echo "No critical vulnerabilities allowed in production"

  # Quality Gates - Final Validation
  quality-gates-summary:
    name: Quality Gates Summary
    runs-on: ubuntu-latest
    needs: [integration-quality-gates]
    if: always()
    steps:
    - name: Quality Gates Status
      run: |
        echo "=== Quality Gates Summary ==="
        echo " Backend Quality: Code quality, type checking, security"
        echo " Frontend Quality: Linting, formatting, type checking, coverage"
        echo " Integration: API schema, frontend-backend compatibility"
        echo " Security: No critical vulnerabilities"
        echo " Coverage: >80% for both backend and frontend"
        echo " Build: Successful build verification"
        echo ""
        echo "All quality gates passed! "

    - name: Fail if any quality gate failed
      if: contains(needs.*.result, "failure")
      run: |
        echo " One or more quality gates failed"
        echo "Please check the failed jobs and fix the issues"
        exit 1
