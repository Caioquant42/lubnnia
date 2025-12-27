#!/usr/bin/env python3
"""
Script to generate comprehensive OPLAB API documentation from OpenAPI spec.
"""
import json
import os
from typing import Dict, List, Any

def extract_endpoint_info(path: str, methods: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract information for all HTTP methods in a path."""
    endpoints = []
    
    for method, details in methods.items():
        if method not in ['get', 'post', 'put', 'delete', 'patch']:
            continue
            
        endpoint_info = {
            'path': path,
            'method': method.upper(),
            'operation_id': details.get('operationId', ''),
            'summary': details.get('summary', ''),
            'description': details.get('description', ''),
            'tags': details.get('tags', []),
            'parameters': [],
            'request_body': None,
            'responses': {},
            'code_sample': None
        }
        
        # Extract parameters
        for param in details.get('parameters', []):
            param_info = {
                'name': param.get('name', ''),
                'in': param.get('in', ''),
                'required': param.get('required', False),
                'description': param.get('description', ''),
                'schema': param.get('schema', {}),
                'example': param.get('example')
            }
            endpoint_info['parameters'].append(param_info)
        
        # Extract request body
        if 'requestBody' in details:
            endpoint_info['request_body'] = details['requestBody']
        
        # Extract responses
        for status_code, response in details.get('responses', {}).items():
            endpoint_info['responses'][status_code] = {
                'description': response.get('description', ''),
                'schema': response.get('content', {}).get('application/json', {}).get('schema', {})
            }
        
        # Extract code sample
        code_samples = details.get('x-codeSamples', [])
        if code_samples:
            endpoint_info['code_sample'] = code_samples[0].get('source', '')
        
        endpoints.append(endpoint_info)
    
    return endpoints

def parse_openapi_spec(file_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """Parse OpenAPI spec and extract all endpoints."""
    with open(file_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    all_endpoints = []
    paths = spec.get('paths', {})
    
    for path, methods in paths.items():
        endpoints = extract_endpoint_info(path, methods)
        all_endpoints.extend(endpoints)
    
    # Organize by category
    market_endpoints = [e for e in all_endpoints if '/market/' in e['path']]
    domain_endpoints = [e for e in all_endpoints if '/domain/' in e['path']]
    
    return {
        'all': all_endpoints,
        'market': market_endpoints,
        'domain': domain_endpoints
    }

def format_parameter(param: Dict[str, Any]) -> str:
    """Format parameter information for markdown."""
    param_type = param['schema'].get('type', 'string')
    required = '**Required**' if param['required'] else 'Optional'
    default = param['schema'].get('default', '')
    default_str = f" (default: `{default}`)" if default else ""
    
    enum = param['schema'].get('enum', [])
    enum_str = f" - Options: `{', '.join(map(str, enum))}`" if enum else ""
    
    return f"- **{param['name']}** ({param['in']}, {param_type}) - {required}{default_str}{enum_str}\n  {param['description']}"

def format_endpoint_markdown(endpoint: Dict[str, Any], implemented_paths: List[str]) -> str:
    """Format a single endpoint as markdown."""
    is_implemented = endpoint['path'] in implemented_paths
    status_badge = "✅ **IMPLEMENTED**" if is_implemented else "❌ Not Implemented"
    
    md = f"### {endpoint['method']} `{endpoint['path']}`\n\n"
    md += f"**Status:** {status_badge}\n\n"
    md += f"**Summary:** {endpoint['summary']}\n\n"
    md += f"**Description:** {endpoint['description']}\n\n"
    
    if endpoint['tags']:
        md += f"**Tags:** {', '.join(endpoint['tags'])}\n\n"
    
    if endpoint['parameters']:
        md += "**Parameters:**\n\n"
        for param in endpoint['parameters']:
            md += format_parameter(param) + "\n\n"
    
    if endpoint['request_body']:
        md += "**Request Body:**\n\n"
        md += "See OpenAPI spec for request body schema.\n\n"
    
    if endpoint['responses']:
        md += "**Responses:**\n\n"
        for status, response in endpoint['responses'].items():
            md += f"- `{status}`: {response['description']}\n"
        md += "\n"
    
    if endpoint['code_sample']:
        md += "**Example Request:**\n\n"
        md += "```bash\n"
        md += endpoint['code_sample'] + "\n"
        md += "```\n\n"
    
    return md

def generate_markdown_docs(endpoints_data: Dict[str, List[Dict[str, Any]]], 
                           implemented_paths: List[str],
                           output_path: str):
    """Generate comprehensive markdown documentation."""
    
    md = """# OPLAB API Methods Overview

This document provides a comprehensive overview of all available methods from the OPLAB API v3, based on the OpenAPI specification.

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Implemented Endpoints](#implemented-endpoints)
4. [Market Endpoints](#market-endpoints)
5. [Domain Endpoints](#domain-endpoints)
6. [Summary Table](#summary-table)

---

## Introduction

The OPLAB REST API provides access to market data, options information, portfolio management, and trading functionality. The API is divided into two main categories:

- **Market**: Market data including quotes, options, stocks, interest rates, historical data, and statistics
- **Domain**: User-related data including portfolios, positions, orders, strategies, watchlists, robots, and notifications

**Base URL:** `https://api.oplab.com.br/v3`

**API Version:** 3.0

---

## Authentication

All API requests require authentication using an access token. The token can be provided in two ways:

1. **HTTP Header** (Recommended):
   ```
   Access-Token: {your-access-token}
   ```

2. **Query Parameter**:
   ```
   ?access_token={your-access-token}
   ```

Access tokens can be obtained from:
- OpLab website: https://go.oplab.com.br/api
- Authentication endpoint: `POST /domain/users/authenticate`

### Error Codes

- `400` - Bad Request: Invalid request parameters
- `401` - Unauthorized: Invalid or missing access token
- `402` - Payment Required: Subscription expired
- `403` - Forbidden: Plan doesn't allow access to this resource
- `404` - Not Found: Route not found
- `412` - Precondition Failed: Action requirements not met
- `422` - Unprocessable Entity: Processing failed
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Server error
- `503` - Service Unavailable: Service temporarily unavailable

---

## Implemented Endpoints

The following endpoints are currently implemented in `backend/app/utils/collar.py`:

"""
    
    # Document implemented endpoints
    implemented_endpoints = [e for e in endpoints_data['all'] if e['path'] in implemented_paths]
    
    for endpoint in implemented_endpoints:
        md += f"### {endpoint['method']} `{endpoint['path']}`\n\n"
        md += f"**Function:** `{get_function_name(endpoint['path'])}`\n\n"
        md += f"**Summary:** {endpoint['summary']}\n\n"
        md += f"**Description:** {endpoint['description']}\n\n"
        md += f"**Implementation:** See `backend/app/utils/collar.py`\n\n"
        md += "---\n\n"
    
    md += "\n## Market Endpoints\n\n"
    md += "Market endpoints provide access to real-time and historical market data.\n\n"
    
    # Group market endpoints by tag
    market_by_tag = {}
    for endpoint in endpoints_data['market']:
        tag = endpoint['tags'][0] if endpoint['tags'] else 'Other'
        if tag not in market_by_tag:
            market_by_tag[tag] = []
        market_by_tag[tag].append(endpoint)
    
    for tag, endpoints in sorted(market_by_tag.items()):
        md += f"### {tag}\n\n"
        for endpoint in endpoints:
            md += format_endpoint_markdown(endpoint, implemented_paths)
            md += "---\n\n"
    
    md += "\n## Domain Endpoints\n\n"
    md += "Domain endpoints provide access to user-specific data and portfolio management.\n\n"
    
    # Group domain endpoints by tag
    domain_by_tag = {}
    for endpoint in endpoints_data['domain']:
        tag = endpoint['tags'][0] if endpoint['tags'] else 'Other'
        if tag not in domain_by_tag:
            domain_by_tag[tag] = []
        domain_by_tag[tag].append(endpoint)
    
    for tag, endpoints in sorted(domain_by_tag.items()):
        md += f"### {tag}\n\n"
        for endpoint in endpoints:
            md += format_endpoint_markdown(endpoint, implemented_paths)
            md += "---\n\n"
    
    # Summary table
    md += "\n## Summary Table\n\n"
    md += "| Method | Path | Summary | Status |\n"
    md += "|--------|------|---------|--------|\n"
    
    for endpoint in sorted(endpoints_data['all'], key=lambda x: (x['path'], x['method'])):
        status = "✅ Implemented" if endpoint['path'] in implemented_paths else "❌ Not Implemented"
        md += f"| {endpoint['method']} | `{endpoint['path']}` | {endpoint['summary']} | {status} |\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"Documentation generated: {output_path}")
    print(f"Total endpoints documented: {len(endpoints_data['all'])}")
    print(f"Market endpoints: {len(endpoints_data['market'])}")
    print(f"Domain endpoints: {len(endpoints_data['domain'])}")
    print(f"Implemented endpoints: {len(implemented_endpoints)}")

def get_function_name(path: str) -> str:
    """Map API path to function name in collar.py."""
    mapping = {
        '/market/options/{symbol}': 'fetch_option_data()',
        '/market/stocks/{symbol}': 'fetch_underlying_data()',
        '/market/interest_rates/{id}': 'fetch_interest_rate()'
    }
    return mapping.get(path, 'N/A')

if __name__ == '__main__':
    # Paths
    openapi_path = 'backend/data-source/oplab_openapi.json'
    output_path = 'docs/OPLAB_API_OVERVIEW.md'
    
    # Implemented paths (without path parameters)
    implemented_paths = [
        '/market/options/{symbol}',
        '/market/stocks/{symbol}',
        '/market/interest_rates/{id}'
    ]
    
    # Parse OpenAPI spec
    print("Parsing OpenAPI specification...")
    endpoints_data = parse_openapi_spec(openapi_path)
    
    # Generate documentation
    print("Generating markdown documentation...")
    generate_markdown_docs(endpoints_data, implemented_paths, output_path)
    
    print("Done!")

