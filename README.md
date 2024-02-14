# Dvorak

Dvorak represents a sophisticated browser credential dumping malware designed to extract local password files from five prominent browsers: Google Chrome, Brave, Firefox, Edge, and Opera GX. Notably, the malware not only gathers these files but also possesses the capability to decrypt them. As of now, Dvorak exclusively decrypts files on Windows systems, while it adeptly collects data from both Windows and Linux platforms. In future endeavors, the focus will shift towards extending the capabilities of Dvorak to include the decryption of files on Linux systems.

https://github.com/brunobertolo/dvorak/assets/50402671/584b0322-fef7-4a83-afa4-c16b6718d63d

## Abstract

Memorising passwords is undoubtedly a challenging task for humans. Consequently, the use of password managers, especially browser-based ones, has seen a noticeable increase in recent years. With that in mind, this paper aims to clarify and conduct an empirical analysis of the security features of password managers in Google Chrome, Microsoft Edge, Opera GX, Mozilla Firefox, and Brave. To corroborate the obtained results, we developed a malware capable of gathering the necessary files to decrypt passwords stored by the browsers and read them in plain text. The results indicate that it is possible to retrieve all the passwords stored in the mentioned browsers in plaintext. In this paper, readers can delve into the details of both the results and the discussion of the security analysis conducted, as well as the processes developed to create the malware. Additionally, relevant open challenges, future work, and conclusions will be presented.

## Contents

Within this repository, you will find an article focusing on **Dvorak: Browser Credential Dumping Malware**, along with the complete code used to craft the malware. A supplementary video is also included, providing a concise summary and consolidation of the practical work conducted. The following list outlines the available file tree in the repository.

- Malware
    - Decrypt.py
    - Main.py
    - Server.py
    - Requirements.txt
- Dvorak_A_Browser_Credential_Dumping_Malware.pdf
- Pratical_Video_Demonstration.mp4

**Note: For the scripts to work there is a need to create a directory "Credentials" in the same directory as "Malware", and a directory for each of the browsers inside the "Credentials" directory. The directories for each of the browsers must be named: edge, chrome, firefox, operagx and brave. The execution of the Main.py script will create zipped credentials inside the directory "Credentials". The user must manually put the zipped files inside the respective browser directories created.**

## Authors

The following authors contributed equally to the work.

- [Bruno Santos](https://github.com/brunobertolo) (_2230456@my.ipleiria.pt_)
- [José Areia](https://github.com/joseareia) (_2230455@my.ipleiria.pt_)

## License

This project is under the [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/) license.
