# SLICKK Mail feature matrix — targets, not claims of completed implementation

Mark each feature VERIFIED only when reproduced against deployed services with tests. Bulwark feature inventory: https://bulwarkmail.org/docs/features ; Stalwart docs: https://stalw.art/docs/.

| Feature | Intended implementation | Current evidence |
|---|---|---|
| Email user accounts/admin | Stalwart internal directory | Not deployed |
| Receive and send externally | Stalwart SMTP + correct MX/PTR/auth/DNS | Not verified; VPS needed |
| Inbox, sent, drafts, trash, spam | Stalwart mailboxes via Bulwark JMAP | Not deployed |
| Rich compose, reply, forward, attachment | Bulwark | Not deployed |
| Search, filters, archive, flag, folders | Bulwark/Stalwart | Not deployed |
| Contacts/address books and groups | Stalwart + Bulwark | Not deployed |
| Calendar, invites, reminders | Stalwart + Bulwark | Not deployed |
| Mobile browser, optional PWA | Bulwark | Not deployed |
| Multi-account, signatures, shortcuts | Bulwark (confirm exact current release) | Not deployed |
| Aliases, custom domains, quotas | Stalwart admin | Not deployed |
| MFA, password recovery, device credentials | Upstream security controls + audited recovery | Not deployed |
| SPF, DKIM, DMARC, anti-spam | Stalwart configuration + actual DNS | Not deployed |
| Invite-only signup/admin approval | Custom wrapper using supported APIs, if required | To implement |
| External customer self-registration | Custom anti-abuse workflow, disabled by default | Blocked until governance |
| Server backups, safe updates, monitoring | Scripts and Codex extensions | Initial scaffolding only |
| Proprietary Gmail AI/Google Workspace features | Not bundled or promised | Excluded/optional future research |

Acceptance must include actual user interaction and message exchange, not a screenshot of a setup wizard alone.
