Fichiers permettant la mise à jour du Pypi pour l'installation en pip




Dans l'ordre :
<ul>
<li>Passer modifictation sur le programme principal ALR32XX.py  
<li>Changer le numéro de version dans Setup.py et ALR32XX/__init.py__
<li>Se positionner dans le dossier et "python Setup.py sdist           <-- création du fichier dist/ALR32XX-1.0.tar
<li>"python setup.py bdist_wheel"                                      <-- création du fichier .whl
<li>"twine upload dist/*"                                              <-- upload des mises à jour.     préalable : pip install twine et pip install wheel
<li>Entrer username et mot de passe 
</ul>
Retrouver les modifs sur : https://pypi.org/project/ALR32XX/#description
</br>
</br>
</br>
Pour créer un pdf à partir d'un readme.md : "grip README.md" dans le fichier courant puis impression du localhost. 
