#!/bin/bash
cd /tmp/gm_audit
rm -f traffic/requests.jsonl
mitmdump -p 8888 -s mitm_addon.py --set block_global=false > mitm.log 2>&1 &
MP=$!
sleep 5
timeout 230 xvfb-run -a -s "-screen 0 1280x800x24" python3 capture_selenium.py > selenium_run.log 2>&1
SE=$?
kill $MP 2>/dev/null
echo "selenium exit: $SE"
wc -l traffic/pw_log.jsonl traffic/requests.jsonl
