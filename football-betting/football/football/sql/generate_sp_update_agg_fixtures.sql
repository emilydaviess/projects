
DROP PROCEDURE IF EXISTS sp_update_agg_fixtures;

CREATE PROCEDURE sp_update_agg_fixtures ()

BEGIN

-- TEAMS WHO PLAY AWAY AGGREGATED RESULTS BY SEASON
INSERT INTO agg_fixture(`season_id`,`team_id`,`team_name`,`wins`,`losses`,`draws`,`goals_for`,`goals_against`,`ht_score_for`,`ht_score_against`,`ft_score_for`,`ft_score_against`)
select 
	a.season_id,
	a.home_team_id, 
	a.team_name,
	SUM(a.wins) + SUM(b.wins) as `wins`, 
	SUM(a.losses) + SUM(b.losses) as `losses`, 
	SUM(a.draws) + SUM(b.draws) as `draws`, 
	SUM(a.goals_for) + SUM(b.goals_for) as `goals_for`, 
	SUM(a.goals_against) + SUM(b.goals_against) as `goals_against`, 
	AVG(a.ht_score_for) + AVG(b.ht_score_for) as `ht_score_for`, 
	AVG(a.ht_score_against) + AVG(b.ht_score_against) as `ht_score_against`, 
	AVG(a.ft_score_for) + AVG(b.ft_score_for) as `ft_score_for`, 
	AVG(a.ft_score_against) + AVG(b.ft_score_against) as `ft_score_for`
from agg_home_fixture a
join agg_away_fixture b on b.season_id = a.season_id and a.home_team_id = b.away_team_id 
group by a.season_id, a.home_team_id
ON DUPLICATE KEY UPDATE team_name=VALUES(`team_name`),wins=VALUES(`wins`),losses=VALUES(`losses`),draws=VALUES(`draws`),goals_for=VALUES(`goals_for`),goals_against=VALUES(`goals_against`),ht_score_for=VALUES(`ht_score_for`),ht_score_against=VALUES(`ht_score_against`),ft_score_for=VALUES(`ft_score_for`),ft_score_against=VALUES(`ft_score_against`); 

END;

