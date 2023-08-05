# G1Race
This package extracts G1 races in horse racing by specifying the SMILE classification.<br>
The original list of G1 races is here: https://www.ifhaonline.org/resources/WTGradedRanking/LWGRank.asp?batch=4 <br>
# 1.How to use
Run the following command to download the package.<br>
$ pip install G1Race<br>
To run the package, use the following command.<br>
$ G1Race<br>
When you first run this package, you will see the text as shown in the image below.<br>
<img width="385" alt="スクリーンショット 2022-01-08 22 23 32" src="https://user-images.githubusercontent.com/60126632/148645836-8a3aff56-bb71-4153-ad2e-d0b10a10be55.png">
<br>
When you see text like the one in this image, enter only one letter, either S, M, I, L, or E.<br>
SMILE is a classification of distance in horse racing, as shown in the table below.<br>
| Category | Meaning | Distance(m) |
| ---- | ---- | ---- |
| S | Sprint | 1000 - 1300 |
| M | Mile | 1301 - 1899 |
| I | Intermediate | 1900 - 2100 |
| L | Long | 2101 - 2700 |
| E | Extended | 2701 - |
<br>
If you select L as an example, you will see the result as shown in the image below.<br>
<img width="698" alt="スクリーンショット 2022-01-08 22 46 13" src="https://user-images.githubusercontent.com/60126632/148646520-301dfedd-8d64-4c3c-9f8b-b8754aab5ef0.png">
<br>
The table at the top of the image shows the top 100 G1 class races in the world in selected categories.<br>
This ranking is determined by the number on the far right of the table, called Rating, which indicates the level of the race. The higher this number, the higher the level of the race, and the more valuable the race is considered to be.<br>
The table at the bottom of the image counts how many races from which country were ranked in the selected category.
