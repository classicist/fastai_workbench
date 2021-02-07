# fastai_workbench
Workbench for Fast.ai course
hi
Don't Do Greek Text Processing on ND machines -- just pre-process it locally, pickle.dump() it onto disk (bz2 zipped up), push it up to the server, and then only do the actual ML and other GPU specific tasks up there. Dont waste your time trying to get python to manage package dependancies in an env you don't own. HUGE waste of time.
