# Fonts

Both fonts ship here and `install.ps1` registers them per-user automatically. No manual
font installation is needed on a new machine.

- **Poppins** — 18 TTF faces, SIL Open Font License.
- **MADE Awelier** — 6 OTF faces. Shipped at the repo owner's explicit direction.

`fontnames.json` maps each file to the exact name it must be registered under, read off a
known-good manual install. **This matters:** Awelier's files are named
`MADEAwelierPERSONALUSE-Bold.otf`, but a correct install registers the face as
`MADE Awelier PERSONAL USE Bold`. Deriving the name from the filename produces a family
CapCut does not recognise, and the title silently renders in the wrong font. If you add or
replace a face, add its real display name to that map.

Installation is per-user: the file is copied to `%LOCALAPPDATA%\Microsoft\Windows\Fonts`
and registered under `HKCU`. No admin rights, and it is exactly where `doctor.py` looks.

**Markerist is not here and cannot be.** It lives only inside CapCut's own effect cache and
arrives when you open `CZ_TEMPLATE` in CapCut while online. There is no filesystem font to
install.
