# Container voor het stadslogistiekrapport (index.html) en het overzicht van
# SUMP/SULP/goederenvervoerplannen (logistics.html). Het themarapport heeft een
# eigen deploy-package: deploy/g40-themas/. Paden moeten overeenkomen met de
# custom locations in Nginx Proxy Manager (proxy_pass zonder URI-rewrite).
FROM nginx:alpine
COPY index.html     /usr/share/nginx/html/g40-stadslogistiek/index.html
COPY logistics.html /usr/share/nginx/html/g40-sump-sulp/index.html
EXPOSE 80
