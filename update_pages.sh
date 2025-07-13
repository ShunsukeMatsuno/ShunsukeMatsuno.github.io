# Bash script to manually trigger the "Deploy Hugo Website to GitHub Pages" workflow using GitHub CLI

# Set these variables as needed
REPO="shunsukematsuno/shunsukematsuno.github.io"  # Replace with your repo if different
WORKFLOW_NAME="Deploy Hugo Website to GitHub Pages"

# Get the workflow file name for the deploy workflow
WORKFLOW_FILE=$(gh workflow list --repo "$REPO" | grep "$WORKFLOW_NAME" | awk '{print $NF}')

if [ -z "$WORKFLOW_FILE" ]; then
  echo "Could not find workflow named '$WORKFLOW_NAME' in $REPO"
  exit 1
fi

# Ask user to confirm
read -p "Are you sure you want to trigger the workflow? [Y/n]: " confirm
confirm=${confirm:-Y}
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Workflow not triggered."
  exit 1
fi

# Trigger the workflow
gh workflow run "$WORKFLOW_FILE" --repo "$REPO"


echo
echo "Triggered workflow '$WORKFLOW_NAME' ($WORKFLOW_FILE) on $REPO"

echo "Run "gh run watch" to watch the deployment job status"
