a = Analysis(
    ['desktop.py'],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
    ],
    hiddenimports=['engineio.async_drivers.threading'],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='TaskTrackr',
    console=False,
)
coll = COLLECT(
    exe, a.binaries, a.datas,
    name='TaskTrackr',
)
