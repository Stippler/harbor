#!/bin/bash

# Check which ports are available and suggest good alternatives

echo "🔍 Checking port availability..."

# Common ports to check
PORTS_TO_CHECK=(7890 8080 8081 8082 8090 9000 9001 9090 3000 4000 5000 7000 7001 7777 8888 9999)

echo ""
echo "Port Status:"
echo "============"

AVAILABLE_PORTS=()

for port in "${PORTS_TO_CHECK[@]}"; do
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        echo "❌ $port - In use"
    else
        echo "✅ $port - Available"
        AVAILABLE_PORTS+=($port)
    fi
done

echo ""
echo "📊 Summary:"
echo "==========="
echo "Available ports: ${AVAILABLE_PORTS[*]}"

if [ ${#AVAILABLE_PORTS[@]} -gt 0 ]; then
    RECOMMENDED=${AVAILABLE_PORTS[0]}
    echo "🌟 Recommended: $RECOMMENDED"
    
    echo ""
    echo "To use port $RECOMMENDED:"
    echo "1. Edit config.json and set port to $RECOMMENDED"
    echo "2. Update firewall: sudo ufw allow $RECOMMENDED/tcp"
    echo "3. Update boat URLs to use port $RECOMMENDED"
else
    echo "⚠️  All checked ports are in use!"
    echo "Try checking higher port numbers (10000+)"
fi

echo ""
echo "Current port usage:"
echo "=================="
netstat -tlnp | grep LISTEN | sort -n -k4
