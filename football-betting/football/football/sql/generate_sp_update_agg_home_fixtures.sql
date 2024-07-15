
DROP PROCEDURE IF EXISTS sp_update_agg_home_fixtures;

CREATE PROCEDURE sp_update_agg_home_fixtures ()

BEGIN

-- TEAMS WHO PLAY HOME AGGREGATED RESULTS BY SEASON
INSERT INTO agg_home_fixture(`season_id`,`home_team_id`,`team_name`,`wins`,`losses`,`draws`,`goals_for`,`goals_against`,`ht_score_for`,`ht_score_against`,`ft_score_for`,`ft_score_against`)
SELECT
	a.season_id,
	a.home_team_id, 
	b.name as `team_name`,
	SUM(c.home_win) as `wins`, 
	SUM(c.away_win) as `losses`, 
	SUM(CASE WHEN c.home_win is NULL THEN 1 ELSE 0 END) as `draws`, 
	SUM(c.home_goals) as `goals_for`, 
	SUM(c.away_goals) as `goals_against`, 
	AVG(c.home_ht_score) as `ht_score_for`,
	AVG(c.away_ht_score) as `ht_score_against`,
	AVG(c.home_ft_score) as `ft_score_for`,
	AVG(c.away_ft_score) as `ft_score_against`
FROM fixture a
JOIN team b on b.id = a.home_team_id 
JOIN fixture_stats c on c.fixture_id = a.id
GROUP BY a.season_id, a.home_team_id
ON DUPLICATE KEY UPDATE team_name=VALUES(`team_name`),wins=VALUES(`wins`),losses=VALUES(`losses`),draws=VALUES(`draws`),goals_for=VALUES(`goals_for`),goals_against=VALUES(`goals_against`),ht_score_for=VALUES(`ht_score_for`),ht_score_against=VALUES(`ht_score_against`),ft_score_for=VALUES(`ft_score_for`),ft_score_against=VALUES(`ft_score_against`); 

END;