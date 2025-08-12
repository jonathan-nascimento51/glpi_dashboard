#!/bin/bash
# Frontend Build Script
set -e

echo "Installing frontend dependencies..."
npm ci

echo "Running security audit..."
npm audit --audit-level=high

echo "Running linting..."
npm run lint

echo "Running type checking..."
npm run type-check

echo "Running tests..."
npm run test

echo "Building for production..."
npm run build

echo "Frontend build completed successfully!"
