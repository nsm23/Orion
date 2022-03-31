"use strict";


const MODERATION_URL = "/moderation/posts/"
const NOTIFICATIONS_HEADER_URL = "/notifications/header/";
const NOTIFICATION_SET_READ_URL = "/notifications/mark-as-read/";
const NOTIFICATION_SET_READ_AND_REDIRECT_URL = "/notifications/mark-as-read/{{model}}/{{id}}/";
const USER_PROFILE_URL = "/cabinet/{{id}}/user_detail/"
const USER_PROFILE_NOTIFICATIONS_URL = "/cabinet/{{id}}/user_comment_notifications/"


const markNotificationReadFetch = ids => {
    const csrftoken = getCookie('csrftoken');
    const request = new Request(NOTIFICATION_SET_READ_URL);
    const options = {
        method: "POST",
        mode: "same-origin",
        body: JSON.stringify({"ids": ids}),
        headers: {"X-CSRFToken": csrftoken, 'Content-Type': 'application/json'}
    };
    return makeFetch(request, options)
}


const markNotificationRead = event => {
    let a = event.target.closest("a");
    if (a.dataset.isRead === "false") {
        return markNotificationReadFetch([a.dataset.objectId])
            .then(response => {
                if (response["ids"]){
                    const notificationsCounterSpan = document.querySelector('#notifications-counter');
                    let count = +notificationsCounterSpan.textContent - 1;
                    notificationsCounterSpan.textContent = count > 0 ? count : "";
                    a.classList.remove("btn-outline-secondary");
                    a.classList.add("btn-success");
                    a.setAttribute("title", "Не прочитано");
                    a.setAttribute("data-is-read", "true");
                }
            })
    }
}


const commentNotificationTemplate = comment => {
    return `
        <li class="row mb-2">
            <div class="col-2 text-center py-2">
                <img class="w-75 rounded-circle" src="${ comment.user_avatar_url }">
            </div>
            <div class="col-8">
                <a href="${ USER_PROFILE_URL.replace('{{id}}', comment.user_id) }" class="text-dark">
                    @${ comment.username }</a>
                <div class="mt-2"><small>${ comment.created_at }</small></div>
                <div>${ comment.text }</div>
            </div>
            <div class="col-2 d-flex flex-column justify-content-center">
                <a title="Прочитано" class="btn btn-sm btn-outline-secondary m-1" 
                    data-is-read="false" data-object-id="${ comment.comment_id }">
                        <i class="bi bi-check-circle-fill mark-as-read" style="font-size: 1rem"></i>
                </a>
                <a href="${ NOTIFICATION_SET_READ_AND_REDIRECT_URL.replace('{{id}}',comment.comment_id).replace('{{model}}', 'comment') }"
                    class="btn btn-sm btn-outline-secondary m-1" 
                    title="Перейти к комментарию">
                        <i class="bi bi-box-arrow-up-right" style="font-size: 1rem"></i>
                </a>
            </div>
        </li>
    `
}


const likeNotificationTemplate = like => {
    let text = '';
    let className = '';
    if (like.vote === 1) {
        text = `<small><i class="bi bi-hand-thumbs-up-fill"></i></small> Понравилась ваша публикация "${like.post_title}"`;
        className = 'text-success';
    }
    else if (like.vote === -1) {
        text = `<small><i class="bi bi-hand-thumbs-down-fill"></i></small> Не понравилась ваша публикация "${like.post_title}`;
        className = 'text-danger';
    }

    return `
        <li class="row mb-2">
            <div class="col-2 text-center py-2">
                <img class="w-75 rounded-circle" src="${ like.user_avatar_url }">
            </div>
            <div class="col-8">
                <a href="${ USER_PROFILE_URL.replace('{{id}}', like.user_id) }" class="text-dark">
                    @${ like.username }</a>
                <div class="${ className }">${ text }</div>
            </div>
            <div class="col-2 d-flex flex-column justify-content-center">
                <a title="Прочитано" data-is-read="false" data-object-id="${ like.like_id }" class="btn btn-sm btn-outline-secondary m-1">
                    <i class="bi bi-check-circle-fill mark-as-read" style="font-size: 1rem"></i>
                </a>
                <a href="${ NOTIFICATION_SET_READ_AND_REDIRECT_URL.replace('{{id}}',like.like_id).replace('{{model}}', 'likedislike') }"
                    title="Перейти к публикации" class="btn btn-sm btn-outline-secondary m-1"  href="">
                    <i class="bi bi-box-arrow-up-right" style="font-size: 1rem"></i>
                </a>
            </div>
        </li>
    `
}


const moderationRequestNotificationTemplate = post => {
    return `
        <li class="row mb-2">
            <div class="col-2 text-center py-2">
                <img class="w-75 rounded-circle" src="${ post.user_avatar_url }">
            </div>
            <div class="col-8">
                <a href="${ USER_PROFILE_URL.replace('{{id}}', post.post_user_id) }" class="text-dark">
                    @${ post.username }</a>
                <div>
                    Публикация "${ post.post_title }" ожидает Вашего одобрения.
                </div>
            </div>
            <div class="col-2 d-flex flex-column justify-content-center">
                <a title="Прочитано" data-is-read="false" data-object-id="${ post.post_id }" class="btn btn-sm btn-outline-secondary m-1">
                    <i class="bi bi-check-circle-fill mark-as-read" style="font-size: 1rem"></i>
                </a>
                <a href="${ NOTIFICATION_SET_READ_AND_REDIRECT_URL.replace('{{id}}',post.post_id).replace('{{model}}', 'post') }"
                    title="Перейти к публикации" class="btn btn-sm btn-outline-secondary m-1"  href="">
                    <i class="bi bi-box-arrow-up-right" style="font-size: 1rem"></i>
                </a>
            </div>
        </li>
    `
}


const moderationNotificationTemplate = obj => {
    let text;
    let icon;
    let className;

    if (obj.content_type === "post") {
        if (obj.decision === "APPROVE") {
            icon = "<i class=\"bi bi-check-lg\"></i>";
            text = `Ваша публикация "${obj.text}" была одобрена.`;
            className = "text-success";
        }
        else if (obj.decision === "DECLINE") {
            icon = "<i class=\"bi bi-x-lg\"></i>";
            text = `Модератор отклонил вашу публикацию "${obj.text}" с комментарием: <br>${obj.comment}`;
            className = "text-danger";
        }
    }
    else
        return;
    return `
        <li class="row mb-2">
            <div class="col-1 text-center ${className}">
                ${ icon }
            </div>
            <div class="col-9 ${ className }">
                ${ text }
            </div>
            <div class="col-2 d-flex flex-column justify-content-center">
                <a title="Прочитано" data-is-read="false" data-object-id="${ obj.id }" class="btn btn-sm btn-outline-secondary m-1">
                    <i class="bi bi-check-circle-fill mark-as-read" style="font-size: 1rem"></i>
                </a>
                <a href="${ NOTIFICATION_SET_READ_AND_REDIRECT_URL.replace('{{id}}',obj.object_id).replace('{{model}}', obj.content_type) }"
                    title="Перейти к публикации" class="btn btn-sm btn-outline-secondary m-1"  href="">
                    <i class="bi bi-box-arrow-up-right" style="font-size: 1rem"></i>
                </a>
            </div>
        </li>
    `
}


const AllNotificationsLinkTemplate = user_id => {
    return `
        <li class="row mt-4 mb-2">
            <div class="col text-center">
                <a href="${ USER_PROFILE_NOTIFICATIONS_URL.replace("{{id}}", user_id) }" class="text-dark">
                    Просмотреть все уведомления
                </a>
            </div>
        </li>
    `
}


const ModerationLinkTemplate = () => {
    return `
        <li class="row mt-4 mb-2">
            <div class="col text-center">
                <a href="${ MODERATION_URL }" class="text-dark">
                    Перейти в раздел модерации
                </a>
            </div>
        </li>
    `
}


const generateNoificationsBar = (params) => {
    // notifications_count, comments, likes, current_user_id
    const notificationsCounterSpan = document.querySelector('#notifications-counter');
    const notificationsUl = document.querySelector('#notifications-ul');

    let notifications_count = params.notifications_count || 0;
    let comments = params.comments || [];
    let likes = params.likes || [];
    let moderation_acts = params.moderation_acts || [];
    let current_user_id = params.current_user_id;
    let complaints = params.complaints || [];

    if (notifications_count > 0)
        notificationsCounterSpan.textContent = notifications_count;

    notificationsUl.innerHTML = '';
    if (comments.length > 0) {
        notificationsUl.innerHTML += "<h5 class='mt-3'>Новые комментарии</h5>";

        for (let comment of comments) {
            let commentLi = commentNotificationTemplate(comment);
            notificationsUl.innerHTML += commentLi;
        }
    }
    if (likes.length > 0) {
        notificationsUl.innerHTML += "<h5 class='mt-3'>Новые оценки</h5>";
        for (let like of likes)
            notificationsUl.innerHTML += likeNotificationTemplate(like);
    }
    if (moderation_acts.length > 0) {
        notificationsUl.innerHTML += "<h5 class='mt-3'>Модерация</h5>";
        for (let act of moderation_acts)
            notificationsUl.innerHTML += moderationNotificationTemplate(act);
    }
    if (complaints.length > 0) {
        notificationsUl.innerHTML += "<h5 class='mt-3'>Новые жалобы</h5>";

        for (let complaint of complaints) {
            let complaintLi = complaintNotificationTemplate(complaint);
            notificationsUl.innerHTML += complaintLi;
        }
    }
    notificationsUl.innerHTML += AllNotificationsLinkTemplate(current_user_id);
}


const generateModerationNotificationBar = (notifications_count, posts) => {
    const moderNotificationCounterSpan = document.querySelector('#moderation-notifications-counter');
    const moderNotificationsUl = document.querySelector('#moderation-notifications-ul');

    if (!moderNotificationsUl)
        return ;

    if (notifications_count > 0)
        moderNotificationCounterSpan.textContent = notifications_count;

    moderNotificationsUl.innerHTML = "";
    if (posts.length > 0) {
        moderNotificationsUl.innerHTML += "<h5 class='mt-3'>Публикации на модерацию</h5>";
        for (let post of posts)
            moderNotificationsUl.innerHTML += moderationRequestNotificationTemplate(post);
    }

    moderNotificationsUl.innerHTML += ModerationLinkTemplate();
}


const getNotifications = () => {
    const request = new Request(NOTIFICATIONS_HEADER_URL);
    const options = {method: "GET", mode: "same-origin"};

    makeFetch(request, options)
        .then(response => {
            if (response["error"])
                console.log(response["error"])
            else {
                generateNoificationsBar({
                    notifications_count: response["notifications_count"],
                    comments: response["comments"],
                    likes: response["likes"],
                    moderation_acts: response["moderation_acts"],
                    current_user_id: response["current_user_id"],
                    complaints: response["complaints"],
                });
                generateModerationNotificationBar(
                    response["posts_to_moderate_count"],
                    response["posts_to_moderate"],
                );
            }
        })
        .then(() => {
                let markAsReadBtns = document.querySelectorAll('.mark-as-read');

                for (let btn of markAsReadBtns) {
                    btn.closest('a').addEventListener("click", event => {
                        event.preventDefault();

                        markNotificationRead(event);
                    })
                }
            }
        )
        .catch()
}

const complaintNotificationTemplate = complaint => {
    return `
        <li class="row mb-2">
            <div class="col-2 text-center py-2">
                <img class="w-75 rounded-circle" src="${ complaint.user_avatar_url }">
            </div>
            <div class="col-8">
                <a href="${ USER_PROFILE_URL.replace('{{id}}', complaint.user_id) }" class="text-dark">
                    @${ complaint.username }</a>
                <div>${ complaint.text }</div>
            </div>
            <div class="col-2 d-flex flex-column justify-content-center">
                <a title="Отметить как прочитано" class="btn btn-sm btn-outline-secondary m-1"
                    data-is-read="false" data-object-id="${ complaint.complaint_id }">
                        <i class="bi bi-check-circle-fill mark-as-read" style="font-size: 1rem"></i>
                </a>
                <a href="${ NOTIFICATION_SET_READ_AND_REDIRECT_URL.replace('{{id}}',complaint.post_id).replace('{{model}}', 'complaint') }"
                    class="btn btn-sm btn-outline-secondary m-1"
                    title="Перейти к статье">
                        <i class="bi bi-box-arrow-up-right" style="font-size: 1rem"></i>
                </a>
            </div>
        </li>
    `
}


document.addEventListener("DOMContentLoaded", event => {
    getNotifications();
});
