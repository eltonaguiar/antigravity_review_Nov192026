# COMS Handoff

## Key Findings
1. **Silent Drops on Publish**: The `send` command reports success even if there are no subscribers, resulting in messages being lost.
   - **Fix**: Use a QoS level to ensure messages are retained.

2. **Partial Registration**: Omitting fields in the `register` command leads to unintended data loss in the roster.
   - **Fix**: Modify the registration to only include keys for supplied flags.

3. **Silent Death on Broker Blips**: The `listen` command fails silently if the broker disconnects.
   - **Fix**: Implement a retry mechanism.

4. **No Non-blocking Read Verb**: Absence of a `check`, `inbox`, or `read` command makes it difficult to access the inbox.
   - **Fix**: Introduce a `COMS check` command.

## Recommendations for Patching
- Prioritize fixing the silent drops on message publishing.
- Ensure the registration behavior is robust to prevent data loss.
- Enhance the `listen` command to provide resilience against disconnections.
- Add a mechanism for reading from the inbox without being blocked.

(End of document)