#!/bin/bash
# pre-commit-validation.sh
#
# This script should be placed in .git/hooks/pre-commit (chmod +x)
# It runs validation checks before allowing commits

set -e

echo "🔍 Running Pre-Commit Validation..."
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Check 1: Python Syntax
echo -e "\n${YELLOW}[1/4] Checking Python syntax...${NC}"
if python -m py_compile *.py questions/*.py app.py math_game.py test_*.py 2>/dev/null; then
    echo -e "${GREEN}✅ Syntax check passed${NC}"
else
    echo -e "${RED}❌ Syntax error found${NC}"
    FAILED=1
fi

# Check 2: Import Verification
echo -e "\n${YELLOW}[2/4] Verifying imports...${NC}"
if python -c "import math_game; import app; import questions" 2>/dev/null; then
    echo -e "${GREEN}✅ All imports successful${NC}"
else
    echo -e "${RED}❌ Import error found${NC}"
    FAILED=1
fi

# Check 3: Run Unit Tests
echo -e "\n${YELLOW}[3/4] Running unit tests...${NC}"
if python -m unittest test_math_game.py test_app.py 2>&1 | grep -q "OK"; then
    echo -e "${GREEN}✅ All tests passed${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo "Run: python -m unittest test_math_game.py test_app.py -v"
    FAILED=1
fi

# Check 4: Method Signature Consistency
echo -e "\n${YELLOW}[4/4] Checking method signature consistency...${NC}"
if python << 'PYEOF'
import re

# Check that add_score calls match signature
def check_add_score_calls():
    files_to_check = [
        ('math_game.py', r'add_score\([^)]+\)'),
        ('app.py', r'add_score\([^)]+\)'),
        ('test_math_game.py', r'add_score\([^)]+\)'),
        ('test_app.py', r'add_score\([^)]+\)')
    ]

    for filename, pattern in files_to_check:
        try:
            with open(filename) as f:
                content = f.read()
                # Look for add_score calls
                matches = re.findall(pattern, content)
                for match in matches:
                    # Check if it has category and difficulty (or defaults)
                    if 'add_score(' in match:
                        # Should have 2-4 parameters
                        params = match.count(',') + 1
                        if params < 2:
                            print(f"❌ Invalid call in {filename}: {match}")
                            return False
        except FileNotFoundError:
            pass

    return True

if check_add_score_calls():
    print("✅ Method calls are consistent")
else:
    print("❌ Method call inconsistency found")
    exit(1)
PYEOF
then
    echo -e "${GREEN}✅ Method signatures consistent${NC}"
else
    echo -e "${RED}❌ Method signature inconsistency${NC}"
    FAILED=1
fi

# Final Result
echo -e "\n=================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All pre-commit checks passed!${NC}"
    echo "Proceeding with commit..."
    exit 0
else
    echo -e "${RED}❌ Pre-commit checks failed!${NC}"
    echo "Please fix the issues above before committing."
    exit 1
fi

