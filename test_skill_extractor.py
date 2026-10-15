
from skill_extractor import extract_skills

# Java must not match JavaScript
skills = extract_skills("Build applications using JavaScript")
assert "JavaScript" in skills
assert "Java" not in skills

# Special characters must match correctly
assert "C++" in extract_skills("Use C++ for development")
assert "C#" in extract_skills("Use C# for development")

# Node.js and Python
assert "Node.js" in extract_skills("Develop applications using Node.js")
assert "Python" in extract_skills("Use Python for automation")

# This should fail until "debug" is added to the
# Debugging aliases in skill_extractor.py
assert "Debugging" in extract_skills("Debug software issues")

print("All dictionary extraction tests passed.")
