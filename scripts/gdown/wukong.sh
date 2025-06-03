#!/bin/bash

BASE_DIR="/nfs/turbo/umd-anglial/GenImageDetector/raw_dataset_zip"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR" || exit

WUKONG_DIR="$BASE_DIR/wukong"
mkdir -p "$WUKONG_DIR"
cd "$WUKONG_DIR" || exit

links=(
  "https://drive.google.com/file/d/1kJWV46KtLv-3ffInvH3C41JXOCkuuxsx/view?usp=drive_link"
  "https://drive.google.com/file/d/1HafVDDUMjMNnPl7AQo_fnIok_P_EeOiM/view?usp=drive_link"
  "https://drive.google.com/file/d/1cZXvQFe7y12hSv3tkKKIQdZb7B1NcQed/view?usp=drive_link"
  "https://drive.google.com/file/d/1F3M68lHsIcq4NrTc3ZaF2ewdZBTIdeDi/view?usp=drive_link"
  "https://drive.google.com/file/d/1H40bbPh4a5NMvvkAeuWXzDlJkujgjEEg/view?usp=drive_link"
  "https://drive.google.com/file/d/1SGnhor2NLsQagZ4yb6CXx4HHjyp01BKd/view?usp=drive_link"
  "https://drive.google.com/file/d/1bTgXOJCkdq9deylfFj11BBmQnHAANODQ/view?usp=drive_link"
  "https://drive.google.com/file/d/1UhxKqGV04OpOgnL6zRKoOtNK0vgmn3SR/view?usp=drive_link"
  "https://drive.google.com/file/d/1cEWWFHPZRRMe1ZAooKITmXUUOnrAu7bp/view?usp=drive_link"
  "https://drive.google.com/file/d/1dR1g5IeHS6JFJo4ilzp3TvumThhf2XMO/view?usp=drive_link"
  "https://drive.google.com/file/d/1A8PrAYREIdKsiBPsP489D1Nh8hPh8yvs/view?usp=drive_link"
  "https://drive.google.com/file/d/1e-1AeoPqcdNbdb2sZxNQqTgLsR9r3utq/view?usp=drive_link"
  "https://drive.google.com/file/d/1OluG52W7j3EA01_GljMTXLhdwFOeiLNR/view?usp=drive_link"
  "https://drive.google.com/file/d/1pDGF0anzsHN0CqfEjBftatWg80UgXU0k/view?usp=drive_link"
  "https://drive.google.com/file/d/1aPNP8rwYsIbjoSGy7LsXi4M2BjRut4VS/view?usp=drive_link"
  "https://drive.google.com/file/d/1nGveKRFP8-4lZp6wXjBL9sPPZqd4oDAt/view?usp=drive_link"
  "https://drive.google.com/file/d/1c01b7DlHGU48SqXG6I7piTIulu1g22Ic/view?usp=drive_link"
  "https://drive.google.com/file/d/1vItmiNv6uZT4-I2UFXjw41_3bTwVb9ys/view?usp=drive_link"
  "https://drive.google.com/file/d/1zdCnRtmDCU_eqcmhDuZUBnFkO5mpMk1F/view?usp=drive_link"
  "https://drive.google.com/file/d/1J1sEF6ZqyRm2gjTZEM2lLjZkf90aD8wj/view?usp=drive_link"
  "https://drive.google.com/file/d/1flrr1KAiwqJht1D6peurBzmOJV2aDHJa/view?usp=drive_link"
  "https://drive.google.com/file/d/1VB3urdLIA4g_9fGYGtymPOmD9-Qrgj_E/view?usp=drive_link"
  "https://drive.google.com/file/d/1qlUDaYVhZNZiqt93P4exDh7HJx_4lI97/view?usp=drive_link"
  "https://drive.google.com/file/d/1iEIwIRKyhmR280bxK13gKUrRmS1vwtoU/view?usp=drive_link"
  "https://drive.google.com/file/d/1Dqjcjdh5aLJOiNcU2SCj7ltaJPt8eUkl/view?usp=drive_link"
  "https://drive.google.com/file/d/1IxiYuiFZv1CjRbX2EfA5Ue2RzW-X_k8S/view?usp=drive_link"
  "https://drive.google.com/file/d/1Ek-iXLHgF-FU6HEHle-yi__A4uFixB86/view?usp=drive_link"
  "https://drive.google.com/file/d/1YEOnUexP1WDE5v3S1pfQxYe96ymniHSA/view?usp=drive_link"
  "https://drive.google.com/file/d/1ATyPwaj8LchogG2YH46rDPMzKMOR8DpM/view?usp=drive_link"
  "https://drive.google.com/file/d/1g52sSil8DV7ajxa81ztW6BxgmKlE3jrR/view?usp=drive_link"
  "https://drive.google.com/file/d/1sdxRyLz13qnGaL27O9J7-JuIHZEO7W2_/view?usp=drive_link"
)

echo "Downloading Wukong dataset..."
for url in "${links[@]}"; do
  echo "Downloading from $url..."
  gdown --fuzzy "$url"
done

echo "All downloads complete!"
