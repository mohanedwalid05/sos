FROM node:20-slim

WORKDIR /app

COPY package*.json ./

# Install dependencies based on NODE_ENV
RUN if [ "$NODE_ENV" = "development" ] ; then \
        npm install ; \
    else \
        npm ci ; \
    fi

COPY . .

# Set default API URL for build if not provided
ARG NEXT_PUBLIC_API_URL=http://backend:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build if production
RUN if [ "$NODE_ENV" = "production" ] ; then \
        npm run build ; \
    fi

EXPOSE 3000

CMD ["npm", "start"] 