"use strict";


const POST_APPROVE_URL = "/moderation/posts/approve/{{post_id}}/";
const POST_DECLINE_URL = "/moderation/posts/decline/{{post_id}}/";
const POST_BAN_URL = "/moderation/posts/ban/{{post_id}}/";


const getPostModerationURL = (post_id, action) => {
    if (action === "approve")
        return POST_APPROVE_URL.replace("{{post_id}}", post_id);
    if (action === "decline")
        return POST_DECLINE_URL.replace("{{post_id}}", post_id);
    if (action === "ban")
        return POST_BAN_URL.replace("{{post_id}}", post_id);
}

const postModerationFetch = (post_id, action, comment) => {
    let url = getPostModerationURL(post_id, action);

    const csrftoken = getCookie('csrftoken');
    const request = new Request(url);
    const options = {
        method: "POST",
        mode: "same-origin",
        headers: {"X-CSRFToken": csrftoken, 'Content-Type': 'application/json'},
        body: {'comment': comment},
    };
    return makeFetch(request, options);
}


const moderationBtnClick = (postId, action, comment) => {
    return postModerationFetch(postId, action, comment)
        .then(response => {
            if ("error" in response)
                console.log(`Post ${action} error: ${response["error"]}`)
            else {
                let moderationBtns = document.querySelectorAll(`#moderation-btns-${ postId } a`);

                for (let btn of moderationBtns) {
                    btn.classList.remove('btn-outline-success');
                    btn.classList.remove('btn-outline-danger');
                    btn.classList.add('disabled');
                    btn.classList.add('btn-outline-secondary');
                    btn.blur();
                }
            }
        })
        .catch(
            // ToDo: catch errors!
        );
}


const moderationLinkClick = (event, action) => {
    event.preventDefault();

    let a = event.target.closest("a");
    let postId = a.dataset.postId;
    return postModerationFetch(postId, action)
        .then(response => {
            if ("error" in response)
                console.log(`Post ${action} error: ${response["error"]}`)
            else {
                let approveLinks = document.querySelectorAll(`.post-approve-link[data-post-id="${postId}"]`);
                let declineLinks = document.querySelectorAll(`.post-decline-link[data-post-id="${postId}"]`);

                for (let inner_btn of approveLinks)
                    inner_btn.classList.add('d-none');
                for (let inner_btn of declineLinks)
                    inner_btn.classList.add('d-none');

                if (action === "approve") {
                    let liBan = document.createElement('li');
                    let aBan = document.createElement('a');
                    aBan.classList.add("dropdown-item", "post-ban-link");
                    aBan.setAttribute("data-post-id", postId);
                    aBan.textContent = "Заблокировать публикацию";
                    a.addEventListener("click", event => {
                        moderationLinkClick(event, "ban")
                    });
                    liBan.appendChild(aBan);
                    a.parentElement.parentElement.appendChild(liBan);
                }
            }
        })
        .catch(
            // ToDo: catch errors!
        );
}


const prepareModal = () => {
    const modalId = "decline-post";
    const modal = document.querySelector(`#${ modalId }`);
    if (!modal)
        return ;
    const modalTitle = modal.querySelector(`#${ modalId }-title`);
    const modalInput = modal.querySelector(`#${ modalId }-input`);
    const modalOkBtn = modal.querySelector(`#${ modalId }-ok-btn`);

    modal.addEventListener("show.bs.modal", event => {
        const button = event.relatedTarget;

        modalOkBtn.textContent = 'Отклонить';
        modalOkBtn.classList.remove('btn-primary');
        modalOkBtn.classList.add('btn-danger');
        modalOkBtn.addEventListener("click", event => {
            event.preventDefault();

            if (!modalInput.value) {
                modalInput.focus();
                return ;
            }
            moderationBtnClick(button.dataset.postId, "decline", modalInput.value).then(() => {
                // ToDo: use close Modal window method
                location.reload();
            });
        });

        modalTitle.textContent = "Отклонить публикацию";
    })
}


document.addEventListener('DOMContentLoaded', event => {
    let postApproveBtns = document.querySelectorAll('.post-approve-btn');
    let postApproveLinks = document.querySelectorAll('.post-approve-link');
    let postDeclineLinks = document.querySelectorAll('.post-decline-link');
    let postBanLinks = document.querySelectorAll('.post-ban-link');

    // Buttons on moderation page
    for (let btn of postApproveBtns)
        btn.addEventListener("click", event => {
            event.preventDefault();
            moderationBtnClick(event.target.closest('a').dataset.postId, "approve");
        });

    // Links in moderation dropdown bar
    for (let link of postApproveLinks)
        link.addEventListener("click", event => {
            event.preventDefault();
            moderationBtnClick(event.target.dataset.postId, "approve").then(() => {
                location.reload();
            });
        });
    for (let link of postBanLinks)
        link.addEventListener("click", event => {
            event.preventDefault();
            moderationBtnClick(event.target.dataset.postId, "ban").then(() => {
                location.reload();
            });
        });

    prepareModal();
})
