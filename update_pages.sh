#!/usr/bin/env bash
# Manually trigger the "Deploy Hugo Website to GitHub Pages" workflow using GitHub CLI,
# then optionally watch the run.

# Set these variables as needed
REPO="shunsukematsuno/shunsukematsuno.github.io"  # Replace with your repo if different
WORKFLOW_NAME="Deploy Hugo Website to GitHub Pages"

# Get the workflow ID for the deploy workflow (last column of `gh workflow list`)
WORKFLOW_ID=$(gh workflow list --repo "$REPO" | grep "$WORKFLOW_NAME" | awk '{print $NF}')

if [ -z "$WORKFLOW_ID" ]; then
  echo "Could not find workflow named '$WORKFLOW_NAME' in $REPO"
  exit 1
fi

# Ask user to confirm
read -r -p "Are you sure you want to trigger the workflow? [Y/n]: " confirm
confirm=${confirm:-Y}
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Workflow not triggered."
  exit 1
fi

# Remember when we triggered it (a few seconds early, to allow for clock skew),
# so we can find the run this trigger created.
since=$(date -u -d '-10 seconds' +%Y-%m-%dT%H:%M:%SZ)

# Trigger the workflow
if ! gh workflow run "$WORKFLOW_ID" --repo "$REPO"; then
  echo "Failed to trigger workflow '$WORKFLOW_NAME'."
  exit 1
fi

echo
echo "Triggered workflow '$WORKFLOW_NAME' ($WORKFLOW_ID) on $REPO"

# `gh workflow run` does not return the run ID, so wait for the new run to appear.
echo -n "Waiting for the run to start"
run_id=""
run_url=""
for _ in $(seq 1 20); do
  read -r run_id run_url < <(
    gh run list --repo "$REPO" --workflow "$WORKFLOW_ID" --event workflow_dispatch \
      --limit 5 --json databaseId,createdAt,url \
      --jq "map(select(.createdAt >= \"$since\")) | .[0] // empty | \"\(.databaseId) \(.url)\"" \
      2>/dev/null
  )
  [ -n "$run_id" ] && break
  echo -n "."
  sleep 3
done
echo

if [ -z "$run_id" ]; then
  echo "Could not find the new run yet. To find and monitor it later, run:"
  echo "  gh run list --repo $REPO --workflow $WORKFLOW_ID --limit 3"
  echo "  gh run watch --repo $REPO"
  exit 0
fi

echo "Run: $run_url"
echo

# Ask whether to monitor now
read -r -p "Do you want to monitor the run now? [Y/n]: " monitor
monitor=${monitor:-Y}
if [[ "$monitor" =~ ^[Yy]$ ]]; then
  gh run watch "$run_id" --repo "$REPO" --exit-status
  status=$?
  echo
  if [ $status -eq 0 ]; then
    echo "Deployment finished successfully."
  else
    echo "Deployment failed. See: $run_url"
    echo "Failed step logs: gh run view $run_id --repo $REPO --log-failed"
  fi
  exit $status
else
  echo "Not monitoring. To monitor it later, run:"
  echo "  gh run watch $run_id --repo $REPO"
fi
