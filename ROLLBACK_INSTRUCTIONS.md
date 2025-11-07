# Rollback Instructions for Integer Index Standardization

**Date:** 2025-11-01
**Branch:** `claude/fix-node-connections-011CUfzkPCRDdhrz3P1TUvxC`
**Commit:** See `git log` on the branch

## What Changed

This update standardized all node indices from `Union[int, str]` to `int` across:
- Backend: All node implementations, NodeConnection, API models
- Frontend: Type definitions, connection handling
- Added defensive validation and logging

## If You Need to Rollback

### Option 1: Revert the Branch (Recommended)

```bash
# Switch back to main branch
git checkout main

# Delete the feature branch locally
git branch -D claude/fix-node-connections-011CUfzkPCRDdhrz3P1TUvxC

# Delete from remote if pushed
git push origin --delete claude/fix-node-connections-011CUfzkPCRDdhrz3P1TUvxC
```

### Option 2: Revert Specific Commits

```bash
# Find the commit hash
git log --oneline

# Revert the changes
git revert <commit-hash>

# Push the revert
git push
```

### Option 3: Cherry-pick Previous State

```bash
# Find the commit BEFORE the integer index changes
git log --oneline

# Create a new branch from that commit
git checkout -b rollback-to-before-integer-indices <previous-commit-hash>

# Push it
git push -u origin rollback-to-before-integer-indices
```

## Files Modified

### Backend (src/):
- `core/node.py` - Base Node class
- `core/node_connection.py` - NodeConnection class
- `core/*_node.py` - All 14+ node implementations
- `api/models.py` - API models (InputInfo, OutputInfo, ConnectionRequest, etc.)
- `api/routers/connections.py` - Connection router validation

### Frontend (src/GUI/src/):
- `apiClient.ts` - Added type validation
- `GraphCanvas.tsx` - Added parsing validation
- `utils/edgeMapping.ts` - Added type checking

### Tests:
- `test_integer_indices.py` - Comprehensive test suite (NEW FILE)

## Symptoms That Require Rollback

If you see any of these issues, you may need to rollback:

1. **Frontend errors in console:**
   - `source_output_index is not a number`
   - `Failed to parse sourceOutputIndex`

2. **Backend errors in logs:**
   - `TypeError: input_index must be int`
   - Connection creation failures

3. **Connection issues:**
   - Can't create connections in UI
   - Connections disappear after creation
   - 422 validation errors from API

## Testing After Rollback

```bash
# Test basic connection creation
python test_connection_session_ids.py

# Test node functionality
cd src/tests
python test_split_1.py
```

## Getting Help

If you need help:
1. Check the GitHub issue tracker
2. Review the commit messages for context
3. Run the test suite: `python test_integer_indices.py`

## Safety Features Added

The following safety features were added to catch issues early:

### Backend Validation:
- Type checking in `Node.set_input()` (src/core/node.py:275-290)
- Index range validation for outputs
- Non-negative index validation

### Frontend Validation:
- Type checking in `apiClient.createConnection()` (src/GUI/src/apiClient.ts:82-90)
- NaN detection in `GraphCanvas.onConnect()` (src/GUI/src/GraphCanvas.tsx:195-202)
- Type warnings in `connectionToEdge()` (src/GUI/src/utils/edgeMapping.ts:17-24)

### Logging:
- Backend: Logs connection creation with indices
- Frontend: Logs parsed indices and types
- Logs validation failures with details

## Verification Commands

```bash
# Check for any remaining Union[int, str] types (should be minimal)
grep -r "Union\[int, str\]" src/

# Verify tests pass
python test_integer_indices.py

# Check connection test
python test_connection_session_ids.py
```
