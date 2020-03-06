#!/bin/sh
# Execute and generate code quality reports

: "${SONAR_HOST_URL:="https://services.dev.bancobari.com.br/sonarqube"}"

if [ -f "./coverage.env" ];
then
  . "./coverage.env"
fi

# Activate virtual environment
if [ -d "ci_env" ]; then
    echo "Activating virtualenv"
    . ci_env/bin/activate
fi

# Get project version
PROJECT_NAME=$(python project.py --project-name)
PROJECT_VERSION=$(python project.py -v)

# Generate pylint-report.txt
pylint src/ \
       -r n \
       --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
       > pylint-report.txt

# Generate coverage.xml
pytest --cov-report xml --cov

# Run sonar-scanner 
sonar-scanner \
  -Dsonar.projectKey=${PROJECT_NAME} \
  -Dsonar.host.url=${SONAR_HOST_URL} \
  -Dsonar.login=${SONAR_LOGIN} \
  -Dsonar.password=${SONAR_PASSWORD} \
  -Dsonar.projectVersion=${PROJECT_VERSION}
