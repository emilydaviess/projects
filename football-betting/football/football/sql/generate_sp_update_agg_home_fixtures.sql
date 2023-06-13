
DROP PROCEDURE IF EXISTS sp_update_agg_home_fixtures;

CREATE PROCEDURE sp_update_agg_home_fixtures (IN startdate DATETIME, IN enddate DATETIME)

BEGIN

-- TEAMS WHO PLAY HOME AGGREGATED RESULTS BY SEASON
SELECT
	a.season,
	a.home_team_id, 
	b.name as `team_name`,
	SUM(c.home_win) as `home_wins`, 
	SUM(c.away_win) as `home_losses`, 
	SUM(CASE WHEN c.home_win is NULL THEN 1 ELSE 0 END) as `home_draws`, 
	SUM(c.home_goals) as `home_goals`, 
	SUM(c.away_goals) as `home_goals_aginst`, 
	AVG(c.home_ht_score) as `home_ht_score_for`,
	AVG(c.away_ht_score) as `home_ht_score_against`,
	AVG(c.home_ft_score) as `home_ft_score_for`,
	AVG(c.away_ft_score) as `home_ft_score_against`
FROM fixture a
JOIN team b on b.id = a.home_team_id 
JOIN fixture_stats c on c.fixture_id = a.id
GROUP BY a.season, a.home_team_id, b.name; 

END;