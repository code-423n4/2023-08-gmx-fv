default: bug

bug_number = `ls mutations/participants | wc -l | tr -d ' '`

.SILENT: bug
bug:
	git diff HEAD -- contracts > mutations/participants/bug$(bug_number).patch
