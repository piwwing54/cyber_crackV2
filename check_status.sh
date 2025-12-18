#!/bin/bash
echo "🔍 CYBER CRACK PRO - REALTIME STATUS CHECK"
echo "=========================================="
docker-compose -f docker-compose-full.yml ps
echo ""
echo "📊 LOG SNIPPET (last 20 lines of orchestrator):"
docker-compose -f docker-compose-full.yml logs --tail=20 orchestrator
