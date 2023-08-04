# Jupyter Notebooks

## Modify Notebooks using SageMaker Studio

### Get to SageMaker Studio

- Go to SageMaker in the AWS console
- Click Studio
- Pick a domain (e.g., `teamphan-sagemaker-testdom`) and profile (e.g.,
  `teamphan-sagemaker-testprof`).
- Click Open Studio

### Configure github in SageMaker studio

Note the "Git" menu item at the top. We will clone our repo to a folder in the
Studio.

- Click on the new dir icon on the left panel (a folder icon with a plus sign).
- Enter a name of the folder (e.g., `codeathon-<your initials>`, replacing
  `<your initials>` with your actual initials.)
- Click on the Git menu, then select "Clone repository".
- Enter as URL:
  <https://github.com/NCBI-Codeathons/vcf-4-population-genomics-team-phan.git>
- For the field "Project directory to clone into": enter the folder your
  created.
- (optional) Uncheck "open README files".
- Click "Clone".

### Create Jupyter Notebooks

- Select File > New > Notebook
- Select an image, and a Kernel
- Click "Select"
- Select File > Save Notebook As
- Save the NB inside the folder Notebooks
- Wait until the NB has been initialized

### Add Notebooks to Github

- Click on Git in the menu bar, then on "Open Git repository in terminal"
- A terminal tab opens
- Create a branch (`git checkout -b <branch name>` replacing `<branch name>`
  with the actual name of the branch you want to use)
- Add the notebook: (`git add Notebooks/<my notebook>.ipynb`, where `<my notebook>`
  is the filename you picked for the NB)
- Commit (`git commit -m 'my test NB' Notebooks/<my notebook>.ipynb`)
- Push (`git push`)
