# Record with: vhs assets/demo.tape
# Produces: assets/demo.gif
#
# This tape assumes `agent-ready` is on PATH (pip install -e . from repo root)
# and is being run from the agent-ready project directory itself.

Output assets/demo.gif

Set Theme "Catppuccin Mocha"
Set FontSize 16
Set Width 1200
Set Height 700
Set TypingSpeed 40ms
Set PlaybackSpeed 1.0
Set Padding 20

Type "# Score any repo on how usable it is to an AI agent."
Enter
Sleep 800ms

Type "agent-ready score ."
Enter
Sleep 2500ms

Type "clear"
Enter
Sleep 300ms

Type "# Failing a check? Ask it how to fix."
Enter
Sleep 600ms

Type "agent-ready explain machine-interface.json-flag-on-commands"
Enter
Sleep 3000ms

Type "clear"
Enter
Sleep 300ms

Type "# Machine-readable when you need it."
Enter
Sleep 600ms

Type "agent-ready score . --json | head -20"
Enter
Sleep 2500ms
