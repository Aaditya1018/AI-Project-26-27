/**
 * SafeStack AI - WebSocket Client Service
 */

export class SafeStackAlertSocket {
  constructor(onAlertCallback) {
    this.onAlert = onAlertCallback;
    this.ws = null;
    this.reconnectTimeout = null;
    this.isClosedManually = false;
  }

  connect() {
    this.isClosedManually = false;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/alerts`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        // Send ping every 25 seconds to keep connection alive
        this.pingInterval = setInterval(() => {
          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send('ping');
          }
        }, 25000);
      };

      this.ws.onmessage = (event) => {
        try {
          if (event.data === 'pong') return;
          const data = JSON.parse(event.data);
          if (data.type === 'NEW_ALERT' && this.onAlert) {
            this.onAlert(data.event);
          }
        } catch (e) {
          // ignore non-json ping/pong
        }
      };

      this.ws.onclose = () => {
        clearInterval(this.pingInterval);
        if (!this.isClosedManually) {
          this.reconnectTimeout = setTimeout(() => this.connect(), 3000);
        }
      };

      this.ws.onerror = () => {
        if (this.ws) this.ws.close();
      };
    } catch (e) {
      this.reconnectTimeout = setTimeout(() => this.connect(), 5000);
    }
  }

  disconnect() {
    this.isClosedManually = true;
    clearInterval(this.pingInterval);
    clearTimeout(this.reconnectTimeout);
    if (this.ws) {
      this.ws.close();
    }
  }
}
