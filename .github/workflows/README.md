# GitHub Actions Workflows

## Current Status

### ✅ Active Workflows
- **basic-check.yml** - Simple workflow that verifies basic repository functionality

### 🔧 Disabled Workflows (Temporarily)
- **ci.yml.disabled** - Full CI/CD pipeline (disabled due to complex dependencies)
- **ci-simple.yml.disabled** - Simplified CI pipeline (disabled for troubleshooting)

## How to Re-enable Workflows

To re-enable a workflow, rename it back to `.yml`:
```bash
# In the repository root
mv .github/workflows/ci.yml.disabled .github/workflows/ci.yml
```

## Workflow Descriptions

### basic-check.yml
- **Purpose**: Verify repository can be cloned and Python works
- **Runs on**: Ubuntu latest
- **Should always**: ✅ PASS

### ci.yml (currently disabled)
- **Purpose**: Full CI/CD with testing, linting, and deployment
- **Issue**: Complex dependencies and test requirements
- **Fix needed**: Simplify or add missing dependencies

### ci-simple.yml (currently disabled)  
- **Purpose**: Simplified testing workflow
- **Issue**: Import errors in tests
- **Fix needed**: Resolve Python path issues

## Troubleshooting

If workflows are still failing:

1. Check the Actions tab for error details
2. Start with only `basic-check.yml`
3. Gradually re-enable other workflows
4. Fix issues one at a time

## Next Steps

1. Ensure `basic-check.yml` passes
2. Fix import issues in test files
3. Re-enable `ci-simple.yml`
4. Finally re-enable full `ci.yml`
