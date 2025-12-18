#!/bin/bash

# Script to fix GitHub SSH connection and upload files to repository
# Repository: https://github.com/piwwing54/cyber_crack.git

echo "Fixing GitHub SSH connection and preparing to upload files..."

# Check if SSH key exists, if not create one
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "Creating new SSH key..."
    ssh-keygen -t rsa -b 4096 -C "piwwing54@gmail.com" -f ~/.ssh/id_rsa -N ""
fi

# Start SSH agent
eval "$(ssh-agent -s)"

# Add SSH key to agent
ssh-add ~/.ssh/id_rsa

# Check if the SSH key is added correctly
ssh-add -l

# Test SSH connection to GitHub
echo "Testing SSH connection to GitHub..."
ssh -T git@github.com

if [ $? -eq 0 ]; then
    echo "SSH connection to GitHub is working!"
else
    echo "SSH connection failed. Please check your SSH key setup."
    exit 1
fi

# Clone or navigate to the repository
REPO_URL="https://github.com/piwwing54/cyber_crack.git"
REPO_DIR="cyber_crack"

if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning repository..."
    git clone $REPO_URL $REPO_DIR
fi

# Navigate to repository directory
cd $REPO_DIR

# Configure git user
git config --global user.email "piwwing54@gmail.com"
git config --global user.name "piwwing54"

# Add all files to git
echo "Adding all files to git..."
git add .

# Commit changes
COMMIT_MSG="Upload files via fix-github-ssh.sh script"
echo "Committing changes: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Add the remote origin if it doesn't exist
if ! git remote get-url origin > /dev/null 2>&1; then
    git remote add origin $REPO_URL
fi

# Push to GitHub
echo "Pushing changes to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "Files successfully uploaded to GitHub!"
else
    echo "Failed to push to GitHub. If this is the first time pushing to a new repository, you may need to create the repository on GitHub first."
    
    # Try with master branch if main doesn't exist
    echo "Trying with master branch..."
    git branch -M master
    git push -u origin master
fi

echo "Done!"