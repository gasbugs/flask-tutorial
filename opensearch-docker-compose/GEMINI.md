# OpenSearch Docker Compose Project

This project provides a multi-node OpenSearch cluster setup using Docker Compose, including OpenSearch Dashboards.

## Project Overview

- **Technologies:** Docker, Docker Compose, OpenSearch, OpenSearch Dashboards.
- **Architecture:** 
  - 3-node OpenSearch cluster (`opensearch-node1`, `opensearch-node2`, `opensearch-node3`).
  - OpenSearch Dashboards for visualization and management.
  - Data persistence using Docker volumes (`opensearch-data1`, `opensearch-data2`, `opensearch-data3`).
  - Tiered storage attributes: `hot`, `warm`, and `cold` assigned to individual nodes.

## Configuration

- **Environment Variables:**
  - `OPENSEARCH_INITIAL_ADMIN_PASSWORD`: Required for the initial setup (must be defined in `.env`).
- **Ports:**
  - `9200`: OpenSearch REST API.
  - `9600`: OpenSearch Performance Analyzer.
  - `5601`: OpenSearch Dashboards UI.

## Building and Running

### Prerequisites
- Docker and Docker Compose installed.
- A `.env` file containing `OPENSEARCH_INITIAL_ADMIN_PASSWORD`.

### Commands
- **Start the cluster:**
  ```bash
  docker-compose up -d
  ```
- **Stop the cluster:**
  ```bash
  docker-compose down
  ```
- **View logs:**
  ```bash
  docker-compose logs -f
  ```
- **Check node status:**
  ```bash
  curl -X GET "https://localhost:9200/_cat/nodes?v" -u "admin:<your_password>" --insecure
  ```

## Development Conventions

- **Storage Tiers:** The nodes are configured with specific storage attributes (`node.attr.temp`):
  - `opensearch-node1`: cold
  - `opensearch-node2`: warm
  - `opensearch-node3`: hot
  - Use these attributes when setting up Index State Management (ISM) policies.
- **Security:** The setup uses default self-signed certificates. Ensure `--insecure` or `-k` is used with `curl` for local testing.
