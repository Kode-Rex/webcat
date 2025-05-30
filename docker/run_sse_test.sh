#!/bin/bash
set -e

echo "🚀 Setting up environment for SSE testing..."

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📄 Loading environment variables from .env file..."
    set -a  # automatically export all variables
    source .env
    set +a
    
    if [ -n "${WEBCAT_API_KEY}" ]; then
        # Mask the key for display
        key_length=${#WEBCAT_API_KEY}
        if [ $key_length -gt 8 ]; then
            masked_key="${WEBCAT_API_KEY:0:4}$(printf '%*s' $((key_length-8)) | tr ' ' '*')${WEBCAT_API_KEY: -4}"
        else
            masked_key="****"
        fi
        echo "✅ Loaded WEBCAT_API_KEY from .env file: ${masked_key}"
    else
        echo "⚠️ WEBCAT_API_KEY not found in .env file"
    fi
    
    if [ -n "${SERPER_API_KEY}" ]; then
        # Mask the key for display
        key_length=${#SERPER_API_KEY}
        if [ $key_length -gt 8 ]; then
            masked_key="${SERPER_API_KEY:0:4}$(printf '%*s' $((key_length-8)) | tr ' ' '*')${SERPER_API_KEY: -4}"
        else
            masked_key="****"
        fi
        echo "✅ Loaded SERPER_API_KEY from .env file: ${masked_key}"
    else
        echo "⚠️ SERPER_API_KEY not found in .env file"
    fi
fi

# Check if API keys are set
if [ -z "${WEBCAT_API_KEY}" ]; then
    echo "⚠️ Warning: WEBCAT_API_KEY environment variable is not set."
    echo "   Please set it with: export WEBCAT_API_KEY=your_api_key"
    echo "   Or add it to your .env file"
    
    # Ask for API key if not set
    read -p "Enter WEBCAT_API_KEY: " input_key
    if [ -n "$input_key" ]; then
        export WEBCAT_API_KEY="$input_key"
        
        # Mask the key for display
        key_length=${#WEBCAT_API_KEY}
        if [ $key_length -gt 8 ]; then
            masked_key="${WEBCAT_API_KEY:0:4}$(printf '%*s' $((key_length-8)) | tr ' ' '*')${WEBCAT_API_KEY: -4}"
        else
            masked_key="****"
        fi
        echo "✅ WEBCAT_API_KEY set to: ${masked_key}"
        
        # Save to .env file
        echo "WEBCAT_API_KEY=$WEBCAT_API_KEY" >> .env
        echo "✅ Saved WEBCAT_API_KEY to .env file"
    else
        echo "❌ No API key provided. Cannot continue."
        exit 1
    fi
fi

# Check if SERPER_API_KEY is set
if [ -z "${SERPER_API_KEY}" ]; then
    echo "⚠️ Warning: SERPER_API_KEY environment variable is not set."
    echo "   Please set it with: export SERPER_API_KEY=your_api_key"
    echo "   Or add it to your .env file"
    
    # Ask for API key if not set
    read -p "Enter SERPER_API_KEY: " input_key
    if [ -n "$input_key" ]; then
        export SERPER_API_KEY="$input_key"
        
        # Mask the key for display
        key_length=${#SERPER_API_KEY}
        if [ $key_length -gt 8 ]; then
            masked_key="${SERPER_API_KEY:0:4}$(printf '%*s' $((key_length-8)) | tr ' ' '*')${SERPER_API_KEY: -4}"
        else
            masked_key="****"
        fi
        echo "✅ SERPER_API_KEY set to: ${masked_key}"
        
        # Save to .env file
        echo "SERPER_API_KEY=$SERPER_API_KEY" >> .env
        echo "✅ Saved SERPER_API_KEY to .env file"
    else
        echo "❌ No API key provided. Cannot continue."
        exit 1
    fi
fi

# Check if Docker container is running
if ! docker ps | grep -q webcat-test; then
    echo "🐳 Starting Docker container for testing..."
    
    # Check if container exists but is stopped
    if docker ps -a | grep -q webcat-test; then
        echo "🔄 Container exists but is not running. Starting it..."
        docker start webcat-test
    else
        echo "🆕 Creating and starting new container..."
        
        # Stop and remove any existing containers
        docker rm -f webcat-test 2>/dev/null || true
        
        # Show the keys being used (masked)
        key_length=${#WEBCAT_API_KEY}
        if [ $key_length -gt 8 ]; then
            masked_key="${WEBCAT_API_KEY:0:4}$(printf '%*s' $((key_length-8)) | tr ' ' '*')${WEBCAT_API_KEY: -4}"
        else
            masked_key="****"
        fi
        echo "🔑 Using WEBCAT_API_KEY: ${masked_key}"
        
        key_length=${#SERPER_API_KEY}
        if [ $key_length -gt 8 ]; then
            masked_key="${SERPER_API_KEY:0:4}$(printf '%*s' $((key_length-8)) | tr ' ' '*')${SERPER_API_KEY: -4}"
        else
            masked_key="****"
        fi
        echo "🔑 Using SERPER_API_KEY: ${masked_key}"
        
        # Run container with environment variables
        echo "🚀 Starting container with API keys..."
        docker run -d --name webcat-test \
            -p 9000:9000 \
            -e PORT=9000 \
            -e WEBCAT_API_KEY="${WEBCAT_API_KEY}" \
            -e SERPER_API_KEY="${SERPER_API_KEY}" \
            -e LOG_LEVEL=DEBUG \
            webcat:latest
        
        if [ $? -ne 0 ]; then
            echo "❌ Failed to start Docker container"
            exit 1
        fi
    fi
    
    # Give the container a moment to start up
    echo "⏳ Waiting for container to start..."
    sleep 5
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "📥 Installing required packages..."
pip install requests sseclient-py

# Run the test using the WebCAT API key
echo "🧪 Running SSE test with WebCAT API key..."
python3 test_sse.py --api-key "${WEBCAT_API_KEY}"

echo "✅ Test completed" 