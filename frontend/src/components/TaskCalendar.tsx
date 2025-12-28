import { useState } from "react";
import type { Task } from "../types";

interface Props {
  tasks: Task[];
  onTaskClick?: (task: Task) => void;
}

export default function TaskCalendar({ tasks, onTaskClick }: Props) {
  const [currentDate, setCurrentDate] = useState(new Date());

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const startingDayOfWeek = firstDayOfMonth.getDay();
  const daysInMonth = lastDayOfMonth.getDate();

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const prevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const getTasksForDate = (day: number): Task[] => {
    return tasks.filter((task) => {
      if (!task.deadline) return false;
      const taskDate = new Date(task.deadline);
      return (
        taskDate.getFullYear() === year &&
        taskDate.getMonth() === month &&
        taskDate.getDate() === day
      );
    });
  };

  const isToday = (day: number): boolean => {
    const today = new Date();
    return (
      today.getFullYear() === year &&
      today.getMonth() === month &&
      today.getDate() === day
    );
  };

  const isPast = (day: number): boolean => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const checkDate = new Date(year, month, day);
    return checkDate < today;
  };

  const renderCalendarDays = () => {
    const days = [];

    // Empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty" />);
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const dayTasks = getTasksForDate(day);
      const pendingTasks = dayTasks.filter((t) => !t.completed);
      const completedTasks = dayTasks.filter((t) => t.completed);

      let dayClass = "calendar-day";
      if (isToday(day)) dayClass += " today";
      if (isPast(day) && !isToday(day)) dayClass += " past";
      if (pendingTasks.length > 0) dayClass += " has-tasks";

      days.push(
        <div key={day} className={dayClass}>
          <span className="day-number">{day}</span>
          {dayTasks.length > 0 && (
            <div className="day-tasks">
              {pendingTasks.slice(0, 3).map((task) => (
                <div
                  key={task.id}
                  className={`calendar-task ${task.effort || "medium"}`}
                  onClick={() => onTaskClick?.(task)}
                  title={task.title}
                >
                  {task.title}
                </div>
              ))}
              {completedTasks.slice(0, 1).map((task) => (
                <div
                  key={task.id}
                  className="calendar-task completed"
                  onClick={() => onTaskClick?.(task)}
                  title={task.title}
                >
                  {task.title}
                </div>
              ))}
              {dayTasks.length > 4 && (
                <div className="more-tasks">
                  +{dayTasks.length - 4} more
                </div>
              )}
            </div>
          )}
        </div>
      );
    }

    return days;
  };

  // Get tasks without deadlines
  const unscheduledTasks = tasks.filter((t) => !t.deadline && !t.completed);

  return (
    <div className="calendar-card">
      <div className="calendar-header">
        <h2>Calendar</h2>
        <div className="calendar-nav">
          <button onClick={prevMonth} className="nav-button">&lt;</button>
          <span className="current-month">
            {monthNames[month]} {year}
          </span>
          <button onClick={nextMonth} className="nav-button">&gt;</button>
          <button onClick={goToToday} className="today-button">Today</button>
        </div>
      </div>

      <div className="calendar-grid">
        {dayNames.map((day) => (
          <div key={day} className="calendar-day-header">
            {day}
          </div>
        ))}
        {renderCalendarDays()}
      </div>

      {unscheduledTasks.length > 0 && (
        <div className="unscheduled-section">
          <h3>No Due Date</h3>
          <div className="unscheduled-tasks">
            {unscheduledTasks.map((task) => (
              <div
                key={task.id}
                className={`calendar-task ${task.effort || "medium"}`}
                onClick={() => onTaskClick?.(task)}
              >
                {task.title}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
