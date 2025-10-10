#!/bin/sh
# Replace __WEBCAT_API_KEY__ placeholder with actual value from env

if [ -n "$WEBCAT_API_KEY" ]; then
    echo "✅ Auth enabled with WEBCAT_API_KEY"
    # Replace map placeholder and add auth check
    sed -i "s|__WEBCAT_API_KEY__|$WEBCAT_API_KEY|g" /etc/nginx/nginx.conf
    sed -i '/# AUTH_CHECK_PLACEHOLDER/c\            if ($auth_valid = 0) { return 401 '"'"'{"error": "Unauthorized"}'"'"'; }' /etc/nginx/nginx.conf
else
    echo "✅ No WEBCAT_API_KEY set - auth disabled"
    # Remove auth check line entirely
    sed -i '/# AUTH_CHECK_PLACEHOLDER/d' /etc/nginx/nginx.conf
fi

# Start supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
