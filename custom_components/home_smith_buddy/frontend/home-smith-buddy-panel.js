/**
 * Home Smith Buddy — sidebar panel.
 *
 * A dependency-free custom element. Home Assistant assigns `hass` and
 * `narrow` properties; on submit it sends the `home_smith_buddy/create_ticket`
 * websocket command, which the integration delivers by email.
 */
class HomeSmithBuddyPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this._rendered) this._render();
  }

  connectedCallback() {
    if (!this._rendered) this._render();
  }

  _render() {
    this._rendered = true;
    this.innerHTML = `
      <style>
        .hsb-wrap {
          max-width: 640px;
          margin: 24px auto;
          padding: 0 16px;
          color: var(--primary-text-color);
          font-family: var(--paper-font-body1_-_font-family, sans-serif);
        }
        .hsb-card {
          background: var(--card-background-color, #fff);
          border-radius: var(--ha-card-border-radius, 12px);
          box-shadow: var(--ha-card-box-shadow, 0 2px 6px rgba(0,0,0,.15));
          padding: 24px;
        }
        h1 { font-size: 1.4rem; margin: 0 0 4px; }
        p.sub { margin: 0 0 20px; color: var(--secondary-text-color); }
        label { display: block; font-weight: 600; margin: 16px 0 6px; }
        input, textarea, select {
          width: 100%;
          box-sizing: border-box;
          padding: 10px 12px;
          font: inherit;
          color: var(--primary-text-color);
          background: var(--secondary-background-color, #f5f5f5);
          border: 1px solid var(--divider-color, #ddd);
          border-radius: 8px;
        }
        textarea { min-height: 140px; resize: vertical; }
        button {
          margin-top: 20px;
          padding: 12px 20px;
          font: inherit;
          font-weight: 600;
          color: var(--text-primary-color, #fff);
          background: var(--primary-color, #03a9f4);
          border: none;
          border-radius: 8px;
          cursor: pointer;
        }
        button:disabled { opacity: .6; cursor: default; }
        .hsb-status { margin-top: 16px; padding: 12px; border-radius: 8px; display: none; }
        .hsb-status.ok { display: block; background: rgba(76,175,80,.15); color: var(--success-color, #4caf50); }
        .hsb-status.err { display: block; background: rgba(244,67,54,.15); color: var(--error-color, #f44336); }
      </style>
      <div class="hsb-wrap">
        <div class="hsb-card">
          <h1>Log a ticket</h1>
          <p class="sub">Send a message to your Home Assistant admin.</p>
          <form id="hsb-form">
            <label for="hsb-subject">Subject</label>
            <input id="hsb-subject" name="subject" required maxlength="120" />

            <label for="hsb-priority">Priority</label>
            <select id="hsb-priority" name="priority">
              <option value="low">Low</option>
              <option value="normal" selected>Normal</option>
              <option value="high">High</option>
            </select>

            <label for="hsb-message">Message</label>
            <textarea id="hsb-message" name="message" required></textarea>

            <button type="submit">Submit ticket</button>
            <div class="hsb-status" id="hsb-status"></div>
          </form>
        </div>
      </div>
    `;
    this._form = this.querySelector("#hsb-form");
    this._status = this.querySelector("#hsb-status");
    this._button = this.querySelector("button");
    this._form.addEventListener("submit", (ev) => this._submit(ev));
  }

  _setStatus(kind, text) {
    this._status.className = `hsb-status ${kind}`;
    this._status.textContent = text;
  }

  async _submit(ev) {
    ev.preventDefault();
    if (!this._hass) return;

    const data = new FormData(this._form);
    this._button.disabled = true;
    this._setStatus("", "");

    try {
      await this._hass.connection.sendMessagePromise({
        type: "home_smith_buddy/create_ticket",
        subject: data.get("subject"),
        message: data.get("message"),
        priority: data.get("priority"),
      });
      this._form.reset();
      this._setStatus("ok", "Ticket sent. Thanks!");
    } catch (err) {
      this._setStatus("err", `Could not send ticket: ${err.message || err}`);
    } finally {
      this._button.disabled = false;
    }
  }
}

customElements.define("home-smith-buddy-panel", HomeSmithBuddyPanel);
