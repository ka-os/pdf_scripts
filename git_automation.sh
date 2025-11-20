#!/bin/bash

# Set color variables for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}--- Step 1: Current Git Status ---${NC}"
git status
echo

# Stage all changes
echo -e "${GREEN}--- Step 2: Staging all changes (git add .) ---${NC}"
git add .
echo "Done."
echo

# Get commit message in a loop
COMMIT_MSG=""
while [ -z "$COMMIT_MSG" ]; do
  read -p "Enter commit message (or press Ctrl+C to cancel): " COMMIT_MSG
  if [ -z "$COMMIT_MSG" ]; then
    echo -e "${YELLOW}Commit message cannot be empty. Please try again.${NC}"
  fi
done

# Commit changes
echo
echo -e "${GREEN}--- Step 3: Committing with message: '$COMMIT_MSG' ---${NC}"
git commit -m "$COMMIT_MSG"
COMMIT_EXIT_CODE=$?
echo

# Check if commit was successful before proceeding
if [ $COMMIT_EXIT_CODE -ne 0 ]; then
    echo -e "${YELLOW}Git commit failed. Aborting script.${NC}"
    exit 1
fi

# Run git status again
echo -e "${GREEN}--- Step 4: Git Status After Commit ---${NC}"
git status
echo

# Ask for confirmation to push
read -p "Do you want to run 'git push'? (y/n): " -n 1 -r
echo # Move to a new line

if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo
  echo -e "${GREEN}--- Step 5: Pushing changes to remote ---${NC}"
  git push
  echo

  # Final git status
  echo -e "${GREEN}--- Step 6: Final Git Status After Push ---${NC}"
  git status
  echo
else
  echo
  echo -e "${YELLOW}Push skipped. You can run 'git push' manually later.${NC}"
fi

echo -e "${GREEN}Script finished.${NC}"
