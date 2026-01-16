# StoryTime API

StoryTime API is a backend service built with Django REST Framework (DRF) that powers a storytelling platform.
It provides secure authentication, email verification, role-based access control, and author management for users who want to create and manage stories.

 

## Features

- JWT Authentication (Login, Refresh, Logout)

- Email verification & resend verification email

- Password reset flow (request & confirm)

- User profile management

- Author profile creation & update

- Role-based access control (Superuser, Admin, Moderator, User)

- Protected endpoints for verified users only

- Stories Caching mechanism (Cache Aside)

- Rate limiting 


## Tech Stack

Backend: Django, Django REST Framework

Authentication: JWT (SimpleJWT + Token Blacklist)

Database: PostgreSQL (recommended)

Task Queue: Celery (for email handling)

Email: SMTP (e.g., Gmail)

Documentation & Testing: Postman

## API Documentation (Postman)

You can explore and test all endpoints using the Postman collection below:

[<img src="https://run.pstmn.io/button.svg" alt="Run In Postman" style="width: 128px; height: 32px;">](https://app.getpostman.com/run-collection/48879534-adba11dc-e4ec-481b-aaca-4383a50c8b84?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D48879534-adba11dc-e4ec-481b-aaca-4383a50c8b84%26entityType%3Dcollection%26workspaceId%3D72f57aef-3c3d-42aa-9120-b8a125dae087)


## AVAILABLE ENDPOINTS

**Note:** Permissions are applied to some endpoints; authentication or role-based access may be required.
### Authentication Endpoints
| Method | Endpoint                            | Description       |
| ------ | ----------------------------------- | ----------------- |
| POST   | `/accounts/register/`               | Register a new user   |
| POST   | `/accounts/login/`               | Login and obtain access & refresh token   |
| POST   | `/accounts/refresh/`                  | Refresh access token   |
| POST   | `/account/logout/`                  | Logout and blacklist refresh token  |

### Email Verification
| Method | Endpoint                            | Description       |
| ------ | ----------------------------------- | ----------------- |
| POST   | `/accounts/resend-email/`               | Resend verification email   |
| GET   | `/accounts/verify/{uid}/<token>/`               | Verify email address   |

### Password Reset

| Method | Endpoint                            | Description       |
| ------ | ----------------------------------- | ----------------- |
| POST   | `/accounts/password-reset/`               | Request password reset email   |
| GET   | `/accounts/reset/{uid}/<token>/`               | Confirm password reset  |

### User & Profile
| Method | Endpoint                            | Description       |
| ------ | ----------------------------------- | ----------------- |
| GET/PATCH   | `/accounts/profile/`               | Retrieve or update user profile|

### Author Management

| Method | Endpoint                            | Description       |
| ------ | ----------------------------------- | ----------------- |
| POST   | `/accounts/register-author/`               | Create an author profile   |
| GET/PATCH   | `/accounts/reset/{uid}/<token>/`               | Retrieve or update author information |

`Each user can have only one author profile.`

### Role Management

| Method | Endpoint                            | Description       |
| ------ | ----------------------------------- | ----------------- |
| PATCH   | `/accounts/users/role/`               | Update user role (Superuser only)   |


### Stories Management

| Method | Endpoint                            | Description       |
| ------ | ----------------------------------- | ----------------- |
| POST   | `/api/stories/`               | Create story   |
| GET   | `/api/stories/`               | List stories |
| GET   | `/api/stories/{story_id}/`               | Fetch story details |
| PUT/PATCH   | `/api/stories/{story_id}/`               | Full or partial story update |
| DELETE  | `/api/stories/{story_id}/`               | Delete story   |

### Stories Reactions
| Method | Endpoint                            | Description       |
| ------ | ----------------------------------- | ----------------- |
| POST  | `/api/stories/{story_id}/reaction/`               | React to story (like or dislike)|
| PATCH  | `/api/stories/{story_id}/reaction/`               | Update story reaction |
| DELETE  | `/api/stories/{story_id}/reaction/`               | Delete story reaction |

### Stories Reviews
| Method | Endpoint                            | Description       |
| ------ | ----------------------------------- | ----------------- |
| POST  | `/api/stories/{story_id}/reviews/`               | Add review to story|
| GET  | `/api/stories/{story_id}/reviews/`               | Fetch all reviews for story|
| GET  | `/api/stories/{story_id}/reviews/{review_id}/`               | Fetch review details |
| PATCH  | `/api/stories/{story_id}/reviews/{review_id}/`               | Update review  |
| DELETE  | `/api/stories/{story_id}/reviews/{review_id}/`               | Delete review |


### Stories Ratings
| Method | Endpoint                            | Description       |
| ------ | ----------------------------------- | ----------------- |
| POST  | `/api/stories/{story_id}/rating/`               | Rate story |
| PATCH  | `/api/stories/{story_id}/rating/`               | Update rating |
| DELETE  | `/api/stories/{story_id}/rating/`               | Delete rating |



### Supported roles:

- user  ---| regular authenticated users, can read and write stories unless banned.

- moderator ---| has permission to delete stories and can request ban of such writer

- admin ---| has permission to delete stories and ban writers

- superuser ---| can do all mentioned above and can change a user's role




### Permissions & Security

| Only authenticated users can access protected endpoints

| Only email-verified users can access certain resources

| Role updates restricted to Superusers

| JWT refresh tokens are blacklisted on logout

| Passwords are securely hashed


▶️ Running Locally
```bash
> git clone https://github.com/JhayceeCodes/StoryTimeAPI
> cd StoryTimeAPI
> python -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt
# create your own .env file using the .env.example as template
> python manage.py migrate
> python manage.py runserver
```

### Future Improvements

- Integration of chapters
- Bookmark system
- Stories cover photo


### Contributing

Contributions are welcome!
Feel free to open issues or submit pull requests.

### License

This project is licensed under the MIT License.