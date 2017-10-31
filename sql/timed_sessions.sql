select * from
(
select ss.title, sl.room, sp.name, sl.date, min(sl.time) as start_time, max(sl.time) as finish_time,
ss.subtitle, ss.track, ss.video, ss.slides, ss.content
from pyconuk_session ss
inner join pyconuk_scheduleslot sl on sl.session_id = ss.id
inner join pyconuk_speaker sp on ss.speaker_id = sp.id
where sl.date like "%28%" and sl.room like "%%"
group by ss.title
) rs 
where rs.start_time <= "12:30" and rs.finish_time >= "12:30"
