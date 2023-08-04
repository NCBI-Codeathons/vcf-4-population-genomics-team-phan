# Jupyter Notebooks

## Authoring Notebooks using SageMaker Studio

### Get to SageMaker Studio

- Open the AWS console, then go to SageMaker
- Click Studio
- Pick a domain (e.g., `teamphan-sagemaker-testdom`) and profile. You should
  create your own profile, but to get started, you could use the profile
  `teamphan-sagemaker-testprof`.
- Click Open Studio

### Configure Github in SageMaker studio

Note the `Git` menu item at the top. We will clone our repo to a folder in the
Studio.

- (optional) To check out a repository in a new subfolder, click on the new
  directory icon on the left panel (a folder icon with a plus sign).

  Enter a name of the folder (e.g., `codeathon-<your initials>`, replacing
  `<your initials>` with your actual initials.)
- Click on the `Git` menu, then select `Clone repository`.
- Enter as URL

  <https://github.com/NCBI-Codeathons/vcf-4-population-genomics-team-phan.git>
- For the field "Project directory to clone into", leave it blank to use the
  root folder, or enter the path of a folder you created.
- (optional) Uncheck "open README files".
- Click "Clone".

### Create Jupyter Notebooks

- Click on `File > New > Notebook`
- Select an image, and a Kernel
- Click `Select`
- Click on `File > Save Notebook As`
- Save the notebook (NB) inside the sub folder `Notebooks` of the repository.
- Wait until the NB has been initialized

### Add Notebooks to Github

- Click on `Git` in the menu bar, then on `Open Git repository in terminal`.
- A terminal tab opens
- Create a branch

  ```bash
  # replace <branch name> with the actual name of the branch you want to use
  git checkout -b <branch name>
  ```

- Add the notebook

  ```bash
  # <my notebook> is the filename you picked for the NB
  git add Notebooks/<my notebook>.ipynb
  ```

- Commit

  ```bash
  git commit -m 'my test NB' Notebooks/<my notebook>.ipynb
  ```

- Push

  ```bash
  git push
  ```
