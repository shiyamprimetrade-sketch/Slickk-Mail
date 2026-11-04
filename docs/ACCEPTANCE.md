# Acceptance tests — none declared passed by package creation

## Static (can be verified before deployment)
- [ ] YAML configurations parse and safe port bindings are asserted.
- [ ] PowerShell files parse on the target Windows environment.
- [ ] Bash scripts syntax-check.
- [ ] No plaintext credentials or private keys in tracked project files.
- [ ] Every planned feature has owner, implementation, test and status.

## Windows local, use real runtime
- [ ] WSL2 Docker Linux engine available; preflight metrics recorded.
- [ ] Stalwart starts and is healthy; setup wizard configured for `slickk.test` local domain.
- [ ] Bulwark loads locally; setup wizard completed with real JMAP endpoint, trusted TLS, correct CORS.
- [ ] Two test accounts log in; send, receive, reply, search, archive and attachment exchanges work.
- [ ] Contacts/calendar tested; missing upstream features documented without fabrication.
- [ ] Two containers restart, mailboxes/contacts/settings survive.
- [ ] Offline backup created, encrypted copy saved, isolated restore validated.
- [ ] Unauthenticated open SMTP relay rejected; registration not publicly open.

## Production, external evidence required
- [ ] Static public IPv4 / provider port 25 in+out / PTR verified.
- [ ] DNS snapshot and migration sign-off saved; no existing mailbox lost.
- [ ] `mail.slickk.online` DNS-only A and PTR; TLS valid.
- [ ] MX, SPF, DKIM and DMARC resolve and match actual sender policies.
- [ ] `inbox.slickk.online` HTTPS works; JMAP CORS/authorization correct.
- [ ] Inbound from independent Gmail reaches target inbox.
- [ ] Outbound to independent Gmail arrives, verified original headers SPF/DKIM/DMARC pass.
- [ ] Outlook roundtrip tested; reject causes documented if not accepted.
- [ ] Uptime, disk, queue, cert and backups are monitored; disaster restore passes.

## Evidence format

For each test: timestamp, environment, exact redacted command, observed output, result, issue/next step. Secret and private message content must be stripped from reports. A deployed login screen alone is not a mail-delivery test.
