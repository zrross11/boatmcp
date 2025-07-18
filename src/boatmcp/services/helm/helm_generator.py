"""Helm chart generation service."""


from boatmcp.schemas.helm import HelmGenerationRequest, HelmGenerationResult
from boatmcp.schemas.repository import ProjectAnalysis


class HelmGenerator:
    """Service for generating Helm charts."""

    async def generate_helm_chart(
        self,
        request: HelmGenerationRequest,
        analysis: ProjectAnalysis
    ) -> HelmGenerationResult:
        """Generate a Helm chart for the given project."""
        try:
            # Validate project path exists
            if not request.project_path.exists():
                return HelmGenerationResult(
                    success=False,
                    error="Project path does not exist"
                )

            # Create helm directory structure
            helm_dir = request.project_path / "helm"
            chart_dir = helm_dir / request.chart_name
            templates_dir = chart_dir / "templates"

            # Create directories
            templates_dir.mkdir(parents=True, exist_ok=True)

            # Generate Chart.yaml
            chart_yaml_content = self._generate_chart_yaml(request)
            (chart_dir / "Chart.yaml").write_text(chart_yaml_content)

            # Generate values.yaml
            values_yaml_content = self._generate_values_yaml(request)
            (chart_dir / "values.yaml").write_text(values_yaml_content)

            # Generate deployment template
            deployment_content = self._generate_deployment_template(request)
            (templates_dir / "deployment.yaml").write_text(deployment_content)

            # Generate service template
            service_content = self._generate_service_template(request)
            (templates_dir / "service.yaml").write_text(service_content)

            # Generate helpers template
            helpers_content = self._generate_helpers_template(request)
            (templates_dir / "_helpers.tpl").write_text(helpers_content)

            return HelmGenerationResult(
                success=True,
                chart_path=chart_dir
            )

        except Exception as e:
            return HelmGenerationResult(
                success=False,
                error=str(e)
            )

    def _generate_chart_yaml(self, request: HelmGenerationRequest) -> str:
        """Generate Chart.yaml content."""
        return f"""apiVersion: v2
name: {request.chart_name}
description: A Helm chart for {request.chart_name}
type: application
version: {request.chart_version}
appVersion: {request.app_version}
"""

    def _generate_values_yaml(self, request: HelmGenerationRequest) -> str:
        """Generate values.yaml content."""
        return f"""# Default values for {request.chart_name}
replicaCount: 1

image:
  repository: {request.image_name}
  pullPolicy: IfNotPresent
  tag: {request.image_tag}

service:
  type: ClusterIP
  port: {request.port}

ingress:
  enabled: false

resources: {{}}

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80

nodeSelector: {{}}

tolerations: []

affinity: {{}}
"""

    def _generate_deployment_template(self, request: HelmGenerationRequest) -> str:
        """Generate deployment template."""
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{{{ include "{request.chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{request.chart_name}.labels" . | nindent 4 }}}}
spec:
  {{{{- if not .Values.autoscaling.enabled }}}}
  replicas: {{{{ .Values.replicaCount }}}}
  {{{{- end }}}}
  selector:
    matchLabels:
      {{{{- include "{request.chart_name}.selectorLabels" . | nindent 6 }}}}
  template:
    metadata:
      labels:
        {{{{- include "{request.chart_name}.selectorLabels" . | nindent 8 }}}}
    spec:
      containers:
        - name: {{{{ .Chart.Name }}}}
          image: "{{{{ .Values.image.repository }}}}:{{{{ .Values.image.tag | default .Chart.AppVersion }}}}"
          imagePullPolicy: {{{{ .Values.image.pullPolicy }}}}
          ports:
            - name: http
              containerPort: {request.port}
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /
              port: http
          readinessProbe:
            httpGet:
              path: /
              port: http
          resources:
            {{{{- toYaml .Values.resources | nindent 12 }}}}
"""

    def _generate_service_template(self, request: HelmGenerationRequest) -> str:
        """Generate service template."""
        return f"""apiVersion: v1
kind: Service
metadata:
  name: {{{{ include "{request.chart_name}.fullname" . }}}}
  labels:
    {{{{- include "{request.chart_name}.labels" . | nindent 4 }}}}
spec:
  type: {{{{ .Values.service.type }}}}
  ports:
    - port: {{{{ .Values.service.port }}}}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{{{- include "{request.chart_name}.selectorLabels" . | nindent 4 }}}}
"""

    def _generate_helpers_template(self, request: HelmGenerationRequest) -> str:
        """Generate _helpers.tpl template."""
        return f"""{{{{/*
Expand the name of the chart.
*/}}}}
{{{{- define "{request.chart_name}.name" -}}}}
{{{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}}}
{{{{- end }}}}

{{{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}}}
{{{{- define "{request.chart_name}.fullname" -}}}}
{{{{- if .Values.fullnameOverride }}}}
{{{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}}}
{{{{- else }}}}
{{{{- $name := default .Chart.Name .Values.nameOverride }}}}
{{{{- if contains $name .Release.Name }}}}
{{{{- .Release.Name | trunc 63 | trimSuffix "-" }}}}
{{{{- else }}}}
{{{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}}}
{{{{- end }}}}
{{{{- end }}}}
{{{{- end }}}}

{{{{/*
Create chart name and version as used by the chart label.
*/}}}}
{{{{- define "{request.chart_name}.chart" -}}}}
{{{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}}}
{{{{- end }}}}

{{{{/*
Common labels
*/}}}}
{{{{- define "{request.chart_name}.labels" -}}}}
helm.sh/chart: {{{{ include "{request.chart_name}.chart" . }}}}
{{{{ include "{request.chart_name}.selectorLabels" . }}}}
{{{{- if .Chart.AppVersion }}}}
app.kubernetes.io/version: {{{{ .Chart.AppVersion | quote }}}}
{{{{- end }}}}
app.kubernetes.io/managed-by: {{{{ .Release.Service }}}}
{{{{- end }}}}

{{{{/*
Selector labels
*/}}}}
{{{{- define "{request.chart_name}.selectorLabels" -}}}}
app.kubernetes.io/name: {{{{ include "{request.chart_name}.name" . }}}}
app.kubernetes.io/instance: {{{{ .Release.Name }}}}
{{{{- end }}}}
"""
