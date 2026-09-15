FROM node:20-slim AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:20-slim
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist

ENV PORT=4173
EXPOSE 4173

CMD ["sh", "-c", "serve -s dist -l ${PORT}"]
