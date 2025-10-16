# Google Cloud Code

## Visão Geral

Cloud Code é uma extensão para VS Code e IntelliJ que traz o poder e conveniência das IDEs para o desenvolvimento de aplicações nativas em nuvem. Cloud Code integra-se com serviços do Google Cloud como Google Kubernetes Engine, Cloud Run, Cloud APIs e Secret Manager.

## Características Principais

### 🚀 Desenvolvimento Kubernetes
- Criação e execução de aplicações em minutos
- Suporte inteligente para YAML do Kubernetes
- Debugging sem configuração
- Execução iterativa run/debug

### ☁️ Desenvolvimento Cloud Run
- Deploy de serviços em minutos
- Monitoramento de progresso com Cloud Run Explorer
- Desenvolvimento local com Cloud Run emulator
- Logs acessíveis diretamente no Log Viewer

### 🐳 Containerização Simplificada
- Imagens seguras e production-ready sem Dockerfile
- Suporte integrado para Google Cloud Buildpacks
- Foco no código da aplicação, não na containerização

### 🔒 Secret Manager Integrado
- Criação, visualização e atualização de secrets
- Uso direto de secrets no código sem exposição
- Gerenciamento seguro de informações sensíveis

### 🔌 APIs do Google Cloud
- Navegação de APIs disponíveis
- Habilitação de serviços
- Instalação e aprendizado de bibliotecas cliente
- Sem sair da IDE

## Instalação

### VS Code
```bash
code --install-extension GoogleCloudTools.cloudcode
```

### IntelliJ
Disponível no marketplace do IntelliJ IDEA.

## Suporte a Linguagens

| Linguagem | Kubernetes | Cloud Run | IntelliJ |
|-----------|------------|-----------|----------|
| Java      | ✅         | ✅        | ✅       |
| Node.js   | ✅         | ✅        | ✅       |
| Go        | ✅         | ✅        | ✅       |
| Python    | ✅         | ✅        | ✅       |
| .NET Core | ✅         | ✅        | ❌       |

## Funcionalidades por IDE

### VS Code
- ✅ Aplicações sample run-ready e debug-ready
- ✅ Suporte para repositórios de templates customizados
- ✅ Múltiplas configurações de run
- ✅ Build e run contínuos
- ✅ Debugging de aplicações Kubernetes
- ✅ Configuração Skaffold editing
- ✅ Suporte avançado YAML Kubernetes
- ✅ Inspeção e browsing de recursos Kubernetes
- ✅ Cloud Run support
- ✅ Cloud Build support
- ✅ Client Library Manager
- ✅ Secret Manager support

### IntelliJ
- ✅ Funcionalidades básicas de Kubernetes
- ✅ Suporte para Java, Node.js, Go, Python
- ✅ Debugging production com snapshots do Cloud Observability
- ✅ Suporte Cloud Storage
- ✅ Suporte App Engine
- ✅ Browser Cloud Storage

## Desenvolvimento Kubernetes

### Criação de Aplicação
1. Abra Command Palette (Ctrl+Shift+P)
2. Execute "Cloud Code: New Application"
3. Escolha template (Go, Java, Node.js, Python, etc.)
4. Configure cluster Kubernetes
5. Execute e debug localmente

### Debugging
- Breakpoints nativos
- Inspeção de variáveis
- Step-through debugging
- Suporte para múltiplos containers

### Desenvolvimento Local
- Minikube integration
- Docker Desktop
- Kind clusters
- Remote clusters

## Desenvolvimento Cloud Run

### Deploy Rápido
1. Abra aplicação
2. Clique direito no arquivo principal
3. "Deploy to Cloud Run"
4. Configure serviço
5. Monitore deploy

### Desenvolvimento Local
- Cloud Run emulator
- Hot reload
- Debugging local
- Testes integrados

## Containerização

### Cloud Buildpacks
- Suporte para Java, Node.js, Go, Python, .NET
- Detecção automática de tipo de aplicação
- Otimização automática de imagens
- Security scanning integrado

### Processo
1. Escreva código da aplicação
2. Cloud Code detecta linguagem/framework
3. Buildpack cria imagem otimizada
4. Deploy para GKE ou Cloud Run

## Secret Manager

### Gerenciamento de Secrets
- Criação via interface
- Visualização de valores
- Atualização segura
- Referenciamento no código

### Uso no Código
```python
# Python
from google.cloud import secretmanager_v1

client = secretmanager_v1.SecretManagerServiceClient()
secret = client.access_secret_version("projects/project/secrets/secret/versions/latest")
```

## APIs do Google Cloud

### Client Library Manager
- Navegação de APIs disponíveis
- Habilitação automática de serviços
- Instalação de bibliotecas cliente
- Snippets de código prontos

### Processo
1. Abra Client Library Manager
2. Navegue por APIs
3. Habilite serviço
4. Instale biblioteca
5. Use no código

## Desenvolvimento Cloud Functions

- Visualização de funções
- Download e deploy
- Teste direto da IDE
- Iteração rápida sem sair do VS Code

## Desenvolvimento Apigee

- Desenvolvimento de API proxies
- Testes unitários e manuais
- Emulador Apigee local
- Iteração rápida build/test

## Compute Engine

- Browse de VMs
- Propriedades relevantes
- SSH direto da IDE
- Transferência de arquivos
- Gerenciamento de VMs

## Uso no Video Genius

O Video Genius utiliza Cloud Code para:

- **Desenvolvimento Kubernetes**: Deploy e debugging de microserviços
- **Cloud Run**: Serviços de processamento de vídeo
- **Secret Manager**: Gerenciamento seguro de credenciais
- **BigQuery APIs**: Integração com dados de vídeo
- **Cloud Storage**: Gerenciamento de arquivos de vídeo
- **Pub/Sub**: Comunicação assíncrona entre serviços

## Configuração

### Pré-requisitos
- Google Cloud SDK instalado
- Autenticação configurada (`gcloud auth login`)
- Projeto GCP selecionado (`gcloud config set project PROJECT_ID`)

### Configurações VS Code
```json
{
  "cloudcode.enableTelemetry": true,
  "cloudcode.kubernetes.logLevel": "info",
  "cloudcode.cloudRun.logLevel": "info"
}
```

## Troubleshooting

### Problemas Comuns
- **Autenticação**: Verificar `gcloud auth list`
- **Projeto**: Confirmar projeto ativo com `gcloud config get-value project`
- **Permissões**: Verificar IAM roles necessárias
- **Clusters**: Verificar conectividade com `kubectl cluster-info`

### Logs e Debug
- Logs do Cloud Code em Output > Cloud Code
- Logs do Kubernetes em Output > Kubernetes
- Debug detalhado com `cloudcode.logLevel`

## Links Úteis

- **Documentação**: https://cloud.google.com/code/docs
- **VS Code**: https://cloud.google.com/code/docs/vscode
- **IntelliJ**: https://cloud.google.com/code/docs/intellij
- **GitHub**: https://github.com/GoogleCloudPlatform/cloud-code-vscode
- **Suporte**: https://cloud.google.com/code/docs/support

## Casos de Uso

- **Desenvolvimento full-stack**: De IDE para produção
- **Microserviços**: Kubernetes e Cloud Run
- **Machine Learning**: MLOps com Vertex AI
- **Data Engineering**: BigQuery e Dataflow
- **DevOps**: CI/CD com Cloud Build

---

*Documentação criada para o projeto Video Genius - Outubro 2025*