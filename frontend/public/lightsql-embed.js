/* LightSQL Embed SDK v1. Application secrets belong only on the host backend. */
;(() => {
  window.LightSQL = {
    mount(options) {
      const origin = new URL(options.baseUrl).origin
      if (!options.container || typeof options.getTicket !== "function")
        throw new Error("container and getTicket are required")
      const instanceId = crypto.randomUUID()
      const frame = document.createElement("iframe")
      frame.title = options.title || "智能问数"
      frame.src = `${origin}/embed/ask?client_id=${encodeURIComponent(options.clientId)}`
      frame.referrerPolicy = "no-referrer"
      frame.setAttribute(
        "sandbox",
        "allow-scripts allow-same-origin allow-forms",
      )
      frame.style.cssText =
        "display:block;width:100%;height:100%;min-height:420px;border:0;border-radius:inherit"
      let destroyed = false
      let authorizing = false
      let sessionId
      let destroyResolve
      let destroyReject
      let destroyTimer
      const sessions = new Set()
      const post = (type, data = {}) =>
        frame.contentWindow?.postMessage(
          { version: 1, instanceId, type, ...data },
          origin,
        )
      const report = (error) =>
        options.onError?.(
          error instanceof Error ? error : new Error(String(error)),
        )
      const remove = () => {
        destroyed = true
        clearInterval(initTimer)
        clearTimeout(destroyTimer)
        window.removeEventListener("message", receive)
        frame.remove()
      }
      const receive = async (event) => {
        const data = event.data
        if (
          destroyed ||
          event.origin !== origin ||
          event.source !== frame.contentWindow ||
          !data ||
          data.version !== 1 ||
          data.instanceId !== instanceId
        )
          return
        if (
          ["ready", "auth_required"].includes(data.type) &&
          typeof data.challenge === "string" &&
          !authorizing
        ) {
          authorizing = true
          clearInterval(initTimer)
          try {
            const response = await options.getTicket({
              origin: location.origin,
              challenge: data.challenge,
              topic_id: options.topicId || null,
            })
            if (!destroyed) {
              post("authenticate", {
                ticket:
                  typeof response === "string" ? response : response.ticket,
              })
              post("context", {
                options: {
                  title: options.title,
                  welcome: options.welcome,
                  theme: options.theme,
                  question: options.question,
                },
              })
            }
          } catch (error) {
            authorizing = false
            report(error)
          }
        } else if (data.type === "authenticated") {
          authorizing = false
          sessionId = data.sessionId
          sessions.add(sessionId)
          options.onSession?.(sessionId)
        } else if (
          data.type === "resize" &&
          options.autoHeight &&
          Number.isFinite(data.height)
        ) {
          frame.style.height = `${Math.max(420, Math.min(1600, data.height))}px`
        } else if (data.type === "destroyed") {
          remove()
          destroyResolve?.()
        } else if (data.type === "error") {
          authorizing = false
          report(data.message)
          if (destroyReject) destroyReject(new Error(data.message))
        }
        options.onEvent?.({ type: data.type, taskId: data.taskId })
      }
      window.addEventListener("message", receive)
      options.container.appendChild(frame)
      const initTimer = setInterval(() => post("init"), 1000)
      frame.addEventListener("load", () => post("init"))
      return {
        open() {
          frame.style.display = "block"
        },
        close() {
          frame.style.display = "none"
        },
        setContext(context) {
          post("context", { options: context })
        },
        async destroy() {
          if (destroyed) return
          if (options.revokeSessions) {
            await options.revokeSessions()
            remove()
            return
          }
          // Backends can revoke every session issued during token renewal.
          if (options.revokeSession) {
            for (const id of sessions) await options.revokeSession(id)
            remove()
            return
          }
          if (sessions.size > 1)
            throw new Error(
              "Provide revokeSession to revoke all renewed sessions before logout",
            )
          if (!sessionId && !authorizing) {
            remove()
            return
          }
          return new Promise((resolve, reject) => {
            destroyResolve = resolve
            destroyReject = reject
            post("destroy")
            destroyTimer = setTimeout(
              () =>
                reject(
                  new Error(
                    "Session revocation unconfirmed; revoke it on your backend",
                  ),
                ),
              5000,
            )
          })
        },
      }
    },
  }
})()
