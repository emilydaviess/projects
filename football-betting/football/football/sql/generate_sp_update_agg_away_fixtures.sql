
DROP PROCEDURE IF EXISTS sp_update_agg_away_fixtures;

CREATE PROCEDURE sp_update_agg_away_fixtures (IN startdate DATETIME, IN enddate DATETIME)

BEGIN

-- TEAMS WHO PLAY AWAY AGGREGATED RESULTS BY SEASON
SELECT
	a.season,
	a.away_team_id, 
	b.name as `team_name`,
	SUM(c.away_win) as `away_wins`, 
	SUM(c.home_win) as `away_losses`, 
	SUM(CASE WHEN c.home_win is NULL THEN 1 ELSE 0 END) as `away_draws`, 
	SUM(c.away_goals) as `away_goals`, 
	SUM(c.home_goals) as `away_goals_aginst`, 
	AVG(c.away_ht_score) as `away_ht_score_for`,
	AVG(c.home_ht_score) as `away_ht_score_against`,
	AVG(c.away_ft_score) as `away_ft_score_for`,
	AVG(c.home_ft_score) as `away_ft_score_against`
FROM fixture a
JOIN team b on b.id = a.away_team_id 
JOIN fixture_stats c on c.fixture_id = a.id
GROUP BY a.season, a.away_team_id, b.name; 

END;

